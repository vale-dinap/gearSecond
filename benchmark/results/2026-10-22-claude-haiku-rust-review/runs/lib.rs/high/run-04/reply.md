I reviewed the file by reading it. I did not compile it or run the tests. The most serious problems are two undefined-behaviour bugs on untrusted input and a lock-order deadlock.

**Undefined behaviour**

- **`SlotTable::lookup` (L185):** `get_unchecked` uses a slot index from a scanner message, so an out-of-range value is an out-of-bounds read. The bounds check is cheap. Use `self.slots.get(slot).copied().flatten()`.
- **`decode` (L218):** `from_utf8_unchecked` runs on network bytes. Invalid UTF-8 produces a `String` with invalid contents, which is UB as soon as it is used. Use `std::str::from_utf8(...)` and map the error to `Malformed`.
- **`append_batch` (L194–197):** `first` is a raw pointer into `buf`'s allocation, taken before `extend_from_slice(tail)`. That call can reallocate, leaving `first` dangling, so the read at L196 is a use-after-free. Even without reallocation, the `&mut` borrow invalidates the raw pointer under Stacked Borrows. The value read is just `head`, so return `head` directly and drop the pointer.

**Panics**

- **`deltas` (L156–157):** The loop runs `i` over `0..prices.len()` and reads `prices[i + 1]`, so the last iteration indexes one past the end. Any non-empty input panics; `deltas(&[5])` panics immediately. Use `prices.windows(2).map(|w| w[1] - w[0])`. The subtraction can also overflow `i64` for extreme inputs, so use `checked_sub` if that matters.
- **`Item::available` (L47):** `on_hand - reserved` underflows whenever `reserved > on_hand`, which `record_loss` can produce. Debug builds panic. Release builds wrap to about 4 billion, so `reserve` (L91) accepts nearly any quantity, and `low_stock` (L132) is also affected.
- **`record_loss` (L120):** `on_hand -= lost` is unchecked, so losing more than is on hand underflows. It also ignores `reserved`, so `reserved <= on_hand` can break silently. Example: on_hand 5, reserved 3, `record_loss(sku, 4)` leaves on_hand 1 and reserved 3, and the next `available()` underflows. Reject or clamp the loss, and decide how losses interact with active holds.
- **`place_hold` (L253):** `Instant::now() + ttl` panics on overflow, for example with `Duration::MAX` from a caller. Use `checked_add` and return an error.
- **`moving_average` (L144):** `assert!` panics on `window == 0` in a public function. That is acceptable only if it is documented under `# Panics`; otherwise return `Result`.

**Concurrency**

- **Lock-order inversion (L245–247 vs L259–265):** `place_hold` and `sweep_expired` take `warehouse` then `holds`. `confirm` takes `holds` then `warehouse`. If one thread is in `confirm` holding `holds` while another is in `place_hold` holding `warehouse`, both block forever. Pick one order everywhere. In `confirm`, take `warehouse` first.
- **Hold consumed before `ship` (L260, L266):** `confirm` removes the hold before `ship` runs. If `ship` fails, the hold is gone, but its units stay counted as reserved with nothing left to release them. With the invariants intact `ship` should not fail, but the `receive` bug below can make it fail. Remove the hold only after success, or restore it on error.
- **Poisoning cascade:** Every lock is `.unwrap()`. One panic while a guard is held, such as the underflow above, poisons the mutex and every later call panics too. Fixing the panics is the real remedy. Handle `PoisonError` explicitly if the service has to keep running after a panic.

**Logic and data integrity**

- **`receive` replaces the entry (L81):** `insert` overwrites an existing SKU, which resets `reserved` to 0 and discards the stored name and price. That contradicts the doc comment at L77–78. Example: `receive(1, "bolt", 10, 25)`, then `reserve(1, 5)`, then `receive(1, "bolt", 10, 25)`. Now `reserved == 0` and `available == 10`, but the outstanding hold still covers 5 units, so 5 units can be sold twice. Use `entry(sku)` and add to `on_hand` for existing items.
- **`encode` truncates the length (L204):** `name.len() as u8` wraps for names over 255 bytes. The length prefix then disagrees with the payload and the frame is misparsed. `receive` accepts names of any length, so this is reachable. Use `u8::try_from` and return an error.
- **`total_value` (L127):** `on_hand as u64 * price_cents` and the `sum()` use unchecked `u64` arithmetic. A large price times a large count overflows, which panics in debug and wraps in release. Use `checked_mul`/`checked_add`, or accumulate in `u128`.

Lower priority, not listed below: `log` grows without bound in a long-running service. `release` saturates silently, and `sweep_expired` discards its error (L278), which hides the inconsistencies above.

ISSUES:
L185: get_unchecked on untrusted slot index is an out-of-bounds read (UB)
L218: from_utf8_unchecked on untrusted network bytes (UB)
L196: read through raw pointer that may dangle after extend_from_slice reallocates (UB)
L157: prices[i + 1] indexes past the end; panics on any non-empty input
L47: available() underflows when reserved > on_hand; wraps in release and lets reserve accept unbounded quantities
L120: record_loss can underflow on_hand and breaks the reserved <= on_hand invariant
L253: Instant + Duration overflow panics on large caller-supplied TTL
L144: assert panics on window == 0 in a public API without documentation
L259: confirm takes holds then warehouse, inverting the lock order used by place_hold and sweep_expired (deadlock)
L266: hold is removed before ship, so a failed ship leaves reserved units with no hold to release them
L81: receive overwrites an existing SKU, resetting reserved and allowing overselling
L204: name.len() as u8 truncates the length prefix for names over 255 bytes, corrupting the frame
L127: unchecked u64 multiplication and sum in total_value can overflow