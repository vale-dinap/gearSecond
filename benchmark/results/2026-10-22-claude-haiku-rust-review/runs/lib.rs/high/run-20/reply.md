I read the module without compiling or running it, so the panic and overflow claims come from reading the code. The most serious problems are two `unsafe` blocks that can cause undefined behaviour on untrusted input, and a `deltas` function that panics on every non-empty input.

## Memory safety / undefined behaviour

**`SlotTable::lookup` (L185):** `get_unchecked` is called with a slot number from a scanner message. Any `slot >= slots.len()` is an out-of-bounds read, which is UB. The `Option` return type also promises `None` for a bad slot, and the code never returns it. The "hot path" comment doesn't justify this. `self.slots.get(slot).copied().flatten()` is a single bounds check.

**`append_batch` (L194–196):** `first` is a raw pointer taken at L194 before `extend_from_slice` at L195. Extending can reallocate `buf`, which leaves `first` dangling, and L196 reads through it. That's a use-after-free that only looks correct when the buffer doesn't grow. The pointer isn't needed: the first SKU is `head`, so `Some((head, buf.len()))` with no `unsafe` is correct.

**`decode` (L218):** `from_utf8_unchecked` runs on bytes from the network. Invalid UTF-8 produces a `String` that violates its invariant, which is UB. Use `std::str::from_utf8(&rest[..len]).map_err(|_| InvError::Malformed("name not UTF-8"))?`.

## Panics and overflow

**`deltas` (L156–157):** The loop runs `0..prices.len()` but reads `prices[i + 1]`. On the last iteration that's `prices[len]`, so every non-empty input panics, including single-element slices. `prices.windows(2).map(|w| w[1] - w[0]).collect()` fixes it. The `i64` subtraction can also overflow for extreme values.

**`Item::available` (L47):** `on_hand - reserved` underflows when `reserved > on_hand`, and that state is reachable. Example: receive 10, hold 8, `record_loss` 5. That leaves `on_hand = 5, reserved = 8`. `available()` panics in debug. In release it wraps to 4294967293, so `reserve` passes its `qty > have` check and oversells. `low_stock` (L132–133) has the same problem.

**`record_loss` (L120):** `on_hand -= lost` is unchecked. In debug, losing more than is on hand panics. In release it wraps to about 4.29 billion and inflates `total_value`. It should reject `lost > available()` with an error.

**`ship` (L112):** `on_hand -= qty` can underflow once `reserved <= on_hand` has been broken, as above.

**`total_value` (L127):** `on_hand as u64 * price_cents` and the `.sum()` are unchecked. Overflow panics in debug and wraps silently in release. Use `checked_mul`/`checked_add` or `u128`.

**`place_hold` (L253):** `Instant::now() + ttl` panics when the sum overflows, for example with `Duration::MAX`. Use `checked_add` and return an error.

**`.unwrap()` on every lock:** If any code panics while holding a guard, such as the underflows above, that mutex is poisoned and every later call on the `Service` panics as well. Either remove the panics or handle poisoning explicitly.

## Concurrency

**Lock-order inversion (L245–247 vs. L259–265 vs. L272–273):** `place_hold` and `sweep_expired` lock `warehouse` then `holds`. `confirm` locks `holds` then `warehouse`. If `confirm` runs at the same time as either of the others, each thread can hold one lock while waiting for the other, which deadlocks. Use one lock order everywhere, or drop the `holds` guard before locking `warehouse`.

## Logic errors

**`receive` (L80–81):** `HashMap::insert` replaces the existing entry. Receiving stock for a known SKU therefore resets `on_hand` to `qty` and zeroes `reserved`, which contradicts the doc comment at L77–78. Outstanding holds still exist, so the warehouse no longer matches them. Use `entry(sku)` and add to `on_hand` for existing SKUs.

**`confirm` (L260–266):** The hold is removed from the map before `ship` runs. If `ship` then fails, for example with `Insufficient` after the reset above, the hold is gone but its units stay in `reserved` permanently. No sweep can release them. Remove the hold only after `ship` succeeds, or put it back on error.

**`encode` (L204):** `name.len() as u8` silently truncates names longer than 255 bytes. The length prefix then disagrees with the bytes that follow, and the peer decodes garbage. Return a `Result`, or reject long names at `receive`.

**`release` (L101):** `saturating_sub` hides over-release, so accounting bugs don't surface. Returning an error when `qty > reserved` would catch them.

**`log` (L82, L113, L121):** The log is never trimmed, so it grows without bound in a long-running service.

## Tests

The existing tests don't cover any of these paths. Useful additions: `deltas` on a one-element slice, out-of-range `lookup`, `receive` on an existing SKU, `record_loss` beyond `on_hand`, encoding a 256-byte name, and `decode` on invalid UTF-8.

ISSUES:
L47: `available()` underflows when reserved exceeds on_hand (panic in debug, wrap in release, oversell)
L80: `receive` overwrites an existing item, discarding its stock and reservations
L82: audit log grows without bound
L112: `ship` subtraction can underflow when the reserved <= on_hand invariant is broken
L120: `record_loss` does not check `lost` against on_hand; underflow/wrap
L127: `total_value` unchecked u64 multiply and sum
L157: `deltas` indexes `prices[len]`; panics on every non-empty input
L185: `get_unchecked` with untrusted slot index; out-of-bounds read (UB)
L194: raw pointer invalidated by `extend_from_slice` reallocation; use-after-free in `append_batch`
L204: `encode` truncates name length to u8; corrupt wire format for names over 255 bytes
L218: `from_utf8_unchecked` on untrusted network bytes (UB)
L253: `Instant::now() + ttl` panics on overflow
L259: lock-order inversion with `place_hold` (L245) and `sweep_expired` (L272); deadlock
L260: `confirm` removes the hold before `ship`; on failure the reservation leaks permanently