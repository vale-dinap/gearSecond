## Review: `src/lib.rs`

I found memory-safety bugs (two `unsafe` blocks misused), a deadlock, and several arithmetic panics and silent corruptions. Line numbers refer to the file as provided.

### Memory safety / undefined behaviour

**`decode`, L218:** `from_utf8_unchecked` runs on bytes from the network. Invalid UTF-8 produces a `String` that violates its invariant, which is undefined behaviour. Use `std::str::from_utf8(&rest[..len]).map_err(|_| InvError::Malformed("bad utf-8"))?`.

**`SlotTable::lookup`, L185:** `get_unchecked` with a `slot` taken from a scanner message. Any slot ≥ `slots.len()` is an out-of-bounds read, which is UB. The "hot path" comment does not make this safe. Use `self.slots.get(slot).copied().flatten()`; the cost is one comparison.

**`append_batch`, L194–197:** `first` is a raw pointer into `buf`, taken before `extend_from_slice(tail)` at L195. That call can reallocate, so the pointer dangles and `*first` at L196 is a use-after-free. The pointer is also unnecessary: the function should return `head` directly.

### Deadlock

**`Service`, L245–247 vs L259–265:** `place_hold` locks `warehouse` then `holds`. `confirm` locks `holds` then `warehouse` (L262 or L265). `sweep_expired` (L272–273) locks `warehouse` then `holds`. Two threads, one in `place_hold` and one in `confirm`, can each hold one lock and wait for the other. Pick one global lock order (for example warehouse, then holds, then next_id) and use it in every method, or put both pieces of state behind a single `Mutex`.

### Panics and arithmetic

**`Item::available`, L47:** `on_hand - reserved` underflows when `reserved > on_hand`, which panics in debug builds and wraps in release. That state is reachable: `record_loss` (L120) can drop `on_hand` below `reserved`. `reserve` (L91), `low_stock` (L132) and the filter all call this.

**`record_loss`, L120:** `on_hand -= lost` is unchecked. Losing more than is on hand panics in debug and wraps in release, leaving `on_hand` near `u32::MAX`. It also lets `on_hand` fall below `reserved`, which causes the L47 panic. Return an error when `lost > on_hand`, and decide what happens to reservations when stock is lost.

**`ship`, L112:** `on_hand -= qty` can underflow for the same reason. The check at L108 only covers `reserved`.

**`deltas`, L157:** `prices[i + 1] - prices[i]` on `i64` overflows for values near `i64::MIN`/`MAX`. Use `checked_sub` or `saturating_sub` and document the choice.

**`total_value`, L127:** `i.on_hand as u64 * i.price_cents` and the `sum()` can overflow `u64`. A large `price_cents` times a large `on_hand` is enough. Use `checked_mul`/`checked_add` and return `Option`, or saturate.

**`place_hold`, L253:** `Instant::now() + ttl` panics if `ttl` is very large (for example `Duration::MAX`). Use `checked_add` and return an error.

**`moving_average`, L144:** `assert!` panics on `window == 0` in a public function. This is a deliberate precondition, but it is a crash on caller input. Return an empty result or an error instead, or document it prominently.

### Data corruption and logic errors

**`receive`, L81:** `insert` replaces the whole `Item`. The doc comment (L77–78) says quantities are added to existing stock, but the code resets `on_hand` to `qty` and `reserved` to 0. Outstanding holds then lose their backing reservation, and later `ship` calls fail with `Insufficient`. Fix it by updating the existing entry (`on_hand = on_hand.checked_add(qty)`, keep `reserved`, update the price and name as intended).

**`confirm`, L260–266:** The hold is removed from the map before `ship` runs. If `ship` fails (for example, the reservation was lost to the L81 bug), the hold is gone but the units stay reserved forever. Remove the hold only after the warehouse operation succeeds.

**`encode`, L204:** `name.len() as u8` silently truncates names longer than 255 bytes. The length prefix then disagrees with the payload, and every following field is misread. Return an error when the name is too long.

**`release`, L101:** `saturating_sub` hides over-release bugs by clamping to zero. This is not a crash, but it can mask accounting errors that the rest of the code assumes cannot happen. Consider returning an error when `qty > reserved`.

### Not defects

`parse_command`, the codec round-trip, and the `try_into().unwrap()` calls in `decode` (guarded by the length check at L215) are correct as written.

Before merging, fix the `unsafe` blocks and the lock order first. Then add tests for `receive` on an existing SKU, `record_loss` beyond `on_hand`, and invalid UTF-8 in `decode`.

ISSUES:
L47: `available()` underflows when `reserved > on_hand` (panic in debug, wrap in release)
L81: `receive` overwrites existing item, resets on_hand and reserved, contradicts doc
L101: `release` saturates silently, masks over-release
L112: `ship` `on_hand -= qty` can underflow
L120: `record_loss` unchecked subtraction, can drop on_hand below reserved
L127: `total_value` u64 multiplication and sum can overflow
L144: `moving_average` asserts on window 0 (panic on caller input)
L157: `deltas` i64 subtraction can overflow
L185: `lookup` uses `get_unchecked` on scanner-supplied slot, out-of-bounds UB
L196: `append_batch` dereferences pointer invalidated by `extend_from_slice` (use-after-free)
L204: `encode` truncates name length to u8, corrupts records over 255 bytes
L218: `decode` uses `from_utf8_unchecked` on untrusted input, UB on invalid UTF-8
L245: `place_hold` locks warehouse then holds, inverted in `confirm`, deadlock risk
L253: `place_hold` `Instant + ttl` panics on very large ttl
L260: `confirm` removes hold before ship, leaks reservation if ship fails