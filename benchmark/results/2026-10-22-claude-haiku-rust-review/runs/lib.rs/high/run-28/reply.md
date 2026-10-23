I read the module without compiling or running it, so the findings below come from reading the code. The worst problems are two undefined-behaviour issues in the `unsafe` blocks and a panic in `deltas` that fires on every non-empty input.

## Memory safety / undefined behaviour

**`decode` (L218).** `from_utf8_unchecked` runs on bytes from the network. Any invalid UTF-8 produces a `String` that violates its invariant, which is UB. Use `std::str::from_utf8(&rest[..len]).map_err(|_| InvError::Malformed("invalid utf-8"))?`.

**`SlotTable::lookup` (L185).** `get_unchecked` takes a slot index from a scanner message, and the doc comment says so. An out-of-range slot reads past the end of the allocation, which is UB even if it doesn't crash. The "hot path" justification doesn't hold up, because the bounds check is negligible. Use `self.slots.get(slot).copied().flatten()`.

**`append_batch` (L194–196).** `first` is computed after `buf.push(head)`. `extend_from_slice(tail)` can reallocate the buffer, which leaves `first` dangling, and then `*first` reads freed memory. The pointer is also unnecessary: the function already has `head`. Return `Some((head, buf.len()))` and drop the `unsafe`.

## Panics and integer overflow

**`deltas` (L156–157).** The loop is `for i in 0..prices.len()` and reads `prices[i + 1]`. On the last iteration that index is `prices.len()`, so the function panics for any input with at least one element. Use `prices.windows(2).map(|w| w[1] - w[0]).collect()`. The subtraction can also overflow for extreme `i64` values, so `checked_sub` may be worth it.

**`Item::available` (L47), `record_loss` (L120), `ship` (L112).** `record_loss` subtracts `lost` from `on_hand` with no check, so `on_hand` can drop below `reserved`. Once that happens, `available()` underflows. In a debug build this panics. In a release build it wraps to a value near `u32::MAX`, which makes a nearly empty SKU look fully stocked and allows overselling. `ship` can then underflow `on_hand` the same way. `record_loss` should reject `lost > on_hand - reserved`, or at least `lost > on_hand`.

**`total_value` (L127).** `on_hand as u64 * price_cents` and the `u64` sum are unchecked. Realistic values won't overflow, but the code has no guard, and a bad price in the data can panic in debug or wrap in release. Use `checked_mul` and `checked_add`, or saturating arithmetic if clamping is acceptable.

**`place_hold` (L253).** `Instant::now() + ttl` panics if the sum overflows, which happens with a very large `Duration`. Use `Instant::now().checked_add(ttl)` and return an error when it is `None`.

## Concurrency

**Lock-order inversion (L245, L247, L259, L262, L265, L272–273).** `place_hold` and `sweep_expired` take `warehouse` and then `holds`. `confirm` takes `holds` and then `warehouse`, and it keeps `holds` locked during the `ship` call. If one thread is in `place_hold` holding `warehouse` and another is in `confirm` holding `holds`, they deadlock. Either pick one lock order everywhere or put `Warehouse` and `holds` behind a single `Mutex`. The second option also makes `place_hold` and `confirm` atomic with respect to each other.

## Logic and data

**`receive` (L79–82, L81).** The doc comment says units are added to an existing SKU, but `items.insert` replaces the whole entry. `on_hand` becomes `qty`, `reserved` drops to 0, and the name and price are overwritten. Existing holds still refer to units that are no longer counted as reserved, so `available()` is overstated and new reservations can oversell. The fix is `entry(sku).or_insert_with(...)` followed by `on_hand += qty`, keeping `reserved` and the price unless the caller says otherwise.

**`confirm` (L260, L266).** The hold is removed from the map before `ship` runs. If `ship` fails (for example, because `reserved` has fallen below `hold.qty`), the error comes back, the hold is gone, and its reservation is never released. This is only reachable after the invariant is broken, such as through the `receive` bug above, but the error path should still release or restore the hold.

**`encode` (L204).** `name.len() as u8` silently truncates names longer than 255 bytes, but the full name is still written. The receiver then reads the wrong length and the rest of the frame is misaligned. Return a `Result` and reject names over 255 bytes, using `u8::try_from(name.len())`.

## Checked, no defect found

`moving_average` (the empty-range and `window > len` cases are handled), `release` (the saturating subtraction is intentional), `snapshot`, `parse_command`, and the `try_into().unwrap()` calls in `decode`, which are safe because the length check comes first.

The existing tests don't exercise any of the paths above, so they will pass with these defects in place.

ISSUES:
L47: available() underflows when reserved exceeds on_hand; debug panic, release wraps to a huge available count
L81: receive() replaces an existing SKU, resetting on_hand and reserved and contradicting its doc comment
L112: ship() can underflow on_hand after record_loss has pushed on_hand below reserved
L120: record_loss() subtracts without a bounds check, so it can underflow and break reserved <= on_hand
L127: total_value() multiplies and sums in u64 without overflow checks
L156: deltas() reads prices[i + 1] with i up to len-1, panicking out of bounds on any non-empty input
L185: lookup() uses get_unchecked on a scanner-supplied index, an out-of-bounds read (UB)
L196: append_batch() dereferences a pointer that dangles if extend_from_slice reallocates (UB)
L204: encode() truncates the name length to u8, so names over 255 bytes produce a corrupt frame
L218: decode() calls from_utf8_unchecked on network bytes, so invalid UTF-8 is UB
L253: place_hold() computes Instant + ttl, which panics on overflow for large ttl
L259: confirm() locks holds then warehouse, while place_hold() and sweep_expired() lock warehouse then holds (deadlock)
L260: confirm() removes the hold before ship(); if ship() fails, the reservation is never released