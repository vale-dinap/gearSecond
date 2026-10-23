I'll review the module for logic errors, panics, overflow, undefined behavior, and concurrency bugs, and check the source so the line numbers match.The module can panic, wrap stock and money, deadlock, and hit undefined behavior on untrusted input. The unsafe codec and slot lookup are the worst of it. `Service` can deadlock and lose reservations. Several stock updates break `on_hand >= reserved`.

### Inventory accounting

`receive` always inserts a brand-new `Item` with `on_hand: qty` and `reserved: 0`. A second receipt of the same SKU replaces the row: previous quantity is discarded, reservations are cleared, and the name and price change. Outstanding holds still believe those units are reserved.

`record_loss` does `on_hand -= lost` with no check. In debug that panics when `lost > on_hand`. In release it wraps. A smaller loss that still eats into reserved units leaves `reserved > on_hand` (10 on hand, 6 reserved, lose 5 → 5 on hand and 6 reserved). `on_hand` and `reserved` are public, so the same state can be built directly.

`available` is `on_hand - reserved`. After that invariant breaks it panics in debug and wraps in release, including through `low_stock` and `reserve`.

`ship` only checks `qty <= reserved`, then subtracts from both counters. With `reserved > on_hand`, `on_hand -= qty` panics or wraps. `reserved` is already reduced if that subtraction panics. Called from `confirm`, the panic also poisons the warehouse mutex.

`release` uses `saturating_sub` and returns `Ok` when `qty` is larger than `reserved`. The extra units are dropped with no `Insufficient` error, so a later `ship` of a real hold can fail.

`total_value` does `on_hand as u64 * price_cents` and sums the products with plain `u64` arithmetic. A large quantity times a large price panics in debug and wraps in release, so the reported value is wrong. `moving_average` has the same class of problem for a window above 2^32 elements of large counts. Its `window == 0` path always asserts, in debug and release.

`deltas` is off by one. The loop is `0..prices.len()` and reads `prices[i + 1]`, so every non-empty slice panics on the last index. The intended bound is already what `saturating_sub(1)` on the capacity is doing. The subtraction is also unchecked `i64` arithmetic, so a swing such as `0 - i64::MIN` panics in debug and wraps in release.

### Undefined behavior

`SlotTable::lookup` calls `get_unchecked` on a slot the comment says comes from a scanner. An out-of-range index is undefined behavior, not `None`. `assign` bounds-checks. `lookup` does not.

`append_batch` saves `buf.as_ptr().wrapping_add(start)` and then `extend_from_slice`s the rest of the batch. If that grows the allocation, the pointer dangles and the unsafe read is a use-after-free. `Sku` is `Copy` and `head` is already the value that pointer was meant to recover. A full buffer and a batch longer than one element triggers it. For example, capacity 1 and batch `[1, 2, 3]`.

`decode` turns network bytes into a `String` with `from_utf8_unchecked`. Invalid UTF-8 is undefined behavior. This should be `str::from_utf8` and `InvError::Malformed`. The later `try_into().unwrap()` calls are safe. The length check really does leave two 4-byte slices.

`encode` stores `name.len() as u8`. A name longer than 255 bytes is truncated in the length prefix (256 becomes 0, 300 becomes 44) while the full byte string is still appended. `decode` then splits the name and the `sku`/`qty` fields at the wrong offset and returns `Ok` with garbage. The round-trip test uses `"nut"`, which hides this.

### Holds and threads

Lock order is inverted:

- `place_hold` and `sweep_expired` lock `warehouse`, then `holds`.
- `confirm` locks `holds`, then `warehouse`.

One thread in `confirm`, holding `holds` and waiting for `warehouse`, and another in `place_hold` or `sweep_expired`, holding `warehouse` and waiting for `holds`, deadlock.

`confirm` removes the hold before `release` or `ship` finishes. If `ship` returns `Insufficient`, or the thread blocks forever on the warehouse lock, the hold is already gone and the units stay reserved with nothing left to confirm or sweep.

`place_hold` calls `reserve` before the hold exists. `Instant::now() + ttl` panics when the deadline does not fit in `Instant` (a huge `ttl`). That panic runs while both mutexes are held, so they poison, every later `lock().unwrap()` panics, and the reservation has no hold.

Integer overflow in this module panics in debug and wraps in release. It is not undefined behavior. The three `unsafe` sites are undefined behavior in both build modes.

ISSUES:
L47: available() subtracts reserved from on_hand unchecked, panicking in debug or wrapping in release once reserved exceeds on_hand
L81: receive() overwrites an existing SKU with on_hand set to qty and reserved set to 0, dropping prior stock and reservations
L101: release() saturates reserved and returns Ok when qty is larger than reserved, so over-release is silently ignored
L112: ship() checks qty only against reserved, so on_hand -= qty panics or wraps when reserved exceeds on_hand, after reserved was already reduced
L120: record_loss() subtracts lost from on_hand with no check, panicking or wrapping, and a loss into reserved stock leaves reserved above on_hand
L127: total_value() multiplies and sums u64 price totals with unchecked arithmetic, panicking in debug or wrapping in release
L144: moving_average() hits assert!(window > 0) and panics for a zero window in debug and release
L157: deltas() reads prices[i + 1] for i in 0..len, so every non-empty slice panics on the last index
L157: deltas() subtracts i64 values unchecked, panicking in debug or wrapping in release when the difference overflows
L185: lookup() uses get_unchecked on a scanner-supplied slot, which is undefined behavior when the index is out of range
L196: append_batch() dereferences a pointer into buf after extend_from_slice can reallocate, which is a use-after-free
L204: encode() stores name.len() as u8, so names longer than 255 bytes get a truncated length and decode as the wrong sku and qty
L218: decode() uses from_utf8_unchecked on network bytes, which is undefined behavior when the name is not UTF-8
L253: Instant::now() + ttl panics on overflow after reserve() has committed, poisoning both mutexes and leaving a reservation with no hold
L260: confirm() removes the hold before release or ship finishes, so a failed ship or a blocked lock leaks reserved units with no hold
L262: confirm() locks holds and then warehouse, while place_hold and sweep_expired lock warehouse and then holds, so those calls deadlock