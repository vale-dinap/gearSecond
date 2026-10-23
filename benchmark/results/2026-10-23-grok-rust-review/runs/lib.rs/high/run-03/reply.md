I'll review the module for logic errors, panics, overflow, undefined behavior, and concurrency bugs.The module has crash bugs, inventory-accounting bugs, and three safe functions that can hit undefined behavior. The existing tests only cover a short happy path, so they miss all of this.

## Inventory accounting

`receive` always `insert`s a brand-new `Item` whose `on_hand` is `qty` and whose `reserved` is 0. A second receipt of the same SKU drops the previous shelf count, the reserved count, the name, and the price. The comment says a second receipt adds units to what is already on hand. Any `Service` hold for that SKU is then stranded: `confirm` will try to ship a quantity that is no longer reserved.

`release` clamps with `saturating_sub` and returns `Ok` when `qty` is larger than `reserved`. That clears every reservation on the SKU, including units held for other callers.

`record_loss` does `on_hand -= lost` with no check. `lost > on_hand` panics in debug and wraps in release. A smaller loss that still eats into reserved units leaves `reserved > on_hand` without panicking. From `on_hand = 10`, `reserved = 8`, `record_loss(5)` ends at `on_hand = 5`, `reserved = 8`.

`available` is `on_hand - reserved`. In that state it panics in debug. In release it wraps to a huge `u32`, and `reserve` will then treat those units as free and can wrap `reserved` again. `low_stock` calls `available`, so it panics on the same state.

`ship` checks `qty` against `reserved` only. In the state above, `ship(6)` passes that check, decrements `reserved`, then panics on `on_hand -= qty`. The reservation is already reduced when the panic happens.

## Overflow

`total_value` does `on_hand as u64 * price_cents` and sums the products in `u64`. Either the multiply or the sum panics in debug and wraps in release, so the reported value is wrong. Two items each worth a little more than half of `u64::MAX` are enough.

`deltas` has two independent failures. The loop is `0..prices.len()` and reads `prices[i + 1]`, so any non-empty slice panics on the last index. The function returns only for an empty slice. `prices[i + 1] - prices[i]` also overflows `i64` on a large swing (`i64::MIN` to `i64::MAX`), which panics in debug and wraps in release.

`moving_average` panics through `assert!` when `window == 0`. The window sum is a `u64`; a window of more than `u64::MAX / u32::MAX` maximum daily counts overflows that sum.

`place_hold` does `Instant::now() + ttl` after `reserve` has already succeeded. `Instant + Duration` panics when the deadline does not fit. Nothing records a hold or undoes the reservation, and the panic poisons the warehouse mutex, so later `lock().unwrap()` calls panic too.

## Undefined behavior in safe functions

`SlotTable::lookup` is a safe method and feeds a handheld-scanner index to `get_unchecked`. An out-of-range slot is undefined behavior, not a bounds-check panic.

`append_batch` saves `buf.as_ptr().wrapping_add(start)`, then calls `extend_from_slice`, then reads that pointer. `extend_from_slice` can reallocate, and the pointer then dangles. The `&mut` borrow also invalidates the pointer even when the allocation stays put. The first SKU is already in `head`, which is `Copy`.

`decode` builds a `String` with `from_utf8_unchecked` on bytes that came off the network. Invalid UTF-8 is undefined behavior.

## Wire format

`encode` stores `name.len() as u8`. A name longer than 255 bytes is written in full, but the length prefix keeps only the low 8 bits. `decode` then treats the middle of the name as the SKU and the quantity. If that truncated prefix splits a multibyte character, the unchecked UTF-8 read is undefined behavior on a round trip of a valid `String`.

## Concurrency

Lock order is inconsistent:

- `place_hold` and `sweep_expired` lock `warehouse`, then `holds`.
- `confirm` locks `holds`, then `warehouse`.

One thread in `place_hold` or `sweep_expired` and another in `confirm` deadlock. `place_hold` has already reserved the units by the time it waits, so those units stay reserved for as long as the deadlock lasts.

`confirm` also `remove`s the hold before `release` or `ship` finishes. If `ship` returns `Insufficient` (reserved count was cleared by `receive`, or reduced below the hold by `release` / `record_loss`), the hold id is gone and the units stay in `reserved` with no hold left to confirm or sweep.

ISSUES:
L47: available does on_hand - reserved, which panics in debug and wraps in release when reserved > on_hand
L81: receive always inserts a new Item, wiping existing on_hand, reserved, name, and price
L101: release saturates and returns Ok when qty > reserved, clearing every reservation on that SKU
L112: ship subtracts qty from on_hand after checking only reserved, so it underflows when on_hand < qty
L120: record_loss does on_hand -= lost with no check, panicking or wrapping and leaving reserved > on_hand
L127: total_value multiplies and sums u64 stock values with no overflow check
L144: moving_average asserts and panics when window is 0
L147: moving_average sums the window in u64 and overflows when the total exceeds u64::MAX
L156: deltas loops 0..prices.len() and panics reading prices[i + 1] on every non-empty slice
L157: deltas subtracts i64 prices and panics in debug or wraps in release on overflow
L185: lookup calls get_unchecked on a scanner-supplied index; out of bounds is undefined behavior
L196: append_batch dereferences a pointer into buf after extend_from_slice, which is use-after-free / undefined behavior
L204: encode stores name.len() as u8, so names longer than 255 bytes decode as the wrong name, SKU, and qty
L218: decode uses from_utf8_unchecked on network bytes; invalid UTF-8 is undefined behavior
L253: Instant::now() + ttl panics on overflow after reserve, leaving stock reserved and poisoning the mutex
L259: confirm locks holds then warehouse while place_hold and sweep_expired lock warehouse then holds, so they deadlock
L260: confirm removes the hold before ship or release finishes, so a failed ship strands reserved units with no hold id