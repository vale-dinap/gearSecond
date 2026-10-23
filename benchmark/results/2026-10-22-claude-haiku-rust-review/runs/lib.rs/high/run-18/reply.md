I found several serious defects: two cases of undefined behaviour, a guaranteed panic in `deltas`, a `receive` that overwrites stock instead of adding to it, and a lock-order inversion that can deadlock. I read the code without compiling it or running the tests.

## Memory safety and undefined behaviour

**`SlotTable::lookup` (L185).** `get_unchecked` is called with `slot`, which the doc comment says comes straight from a handheld scanner message. Any out-of-range value is an out-of-bounds read, which is UB. The "hot path" comment doesn't justify it, since `self.slots.get(slot).copied().flatten()` is just as cheap. Use the checked form.

**`append_batch` (L194–197).** `first` is a raw pointer into `buf` computed after `push`. `extend_from_slice(tail)` can reallocate the buffer, which leaves `first` dangling. `unsafe { *first }` then reads freed memory. The value read is also just `head`, so the pointer is unnecessary. Replace the body with:

```rust
let &head = batch.first()?;
buf.extend_from_slice(batch);
Some((head, buf.len()))
```

**`decode` (L218).** `from_utf8_unchecked` runs on bytes from the network without validation. Invalid UTF-8 produces an invalid `str`, which is UB as soon as it is used, and `.to_string()` copies it. Use `std::str::from_utf8(...).map_err(|_| InvError::Malformed("invalid utf-8"))?`.

## Panics and overflow

**`deltas` (L156–157) always panics on non-empty input.** The loop runs `i` over `0..prices.len()`, so `prices[i + 1]` reads one past the end on the last iteration. Use `prices.windows(2).map(|w| w[1] - w[0]).collect()`. The subtraction can still overflow `i64` for extreme values, so use `checked_sub` or widen to `i128` if that matters.

**`Item::available` (L47) and `record_loss` (L120).** `record_loss` subtracts `lost` from `on_hand` without checking it, and nothing ensures `reserved <= on_hand` afterwards. If `lost > on_hand`, the subtraction panics in debug and wraps to about 4 billion in release. If `lost` leaves less than `reserved`, `available()` underflows, and in release it wraps to a huge value, so `reserve` accepts almost any quantity. Check `lost <= item.available()` and return `Insufficient` otherwise.

**`total_value` (L127).** `on_hand as u64 * price_cents` and the `sum()` can overflow `u64`. A few large-priced items are enough. Use `checked_mul` and `checked_add`, or `u128`.

**`place_hold` (L253).** `Instant::now() + ttl` panics when `ttl` is very large (for example, `Duration::MAX`), and `ttl` is caller input. Use `Instant::now().checked_add(ttl)` and return an error.

**`encode` (L204).** `name.len() as u8` silently truncates names longer than 255 bytes. The length byte then disagrees with the bytes that follow, and the record is corrupt. Make `encode` return `Result` and reject long names with `u8::try_from`.

## Logic errors

**`receive` (L80–81) replaces the existing item.** The doc comment says units are added to stock already on hand, but `insert` overwrites `on_hand`, resets `reserved` to 0, and replaces the name and price. Receiving 10 units of a SKU with 100 on hand leaves 10. Live holds for that SKU also lose their backing reservation, which leads to the saturating-release problem below. Update the existing entry: add to `on_hand`, keep `reserved`, and update the name and price.

**`release` (L101) hides invariant violations.** `saturating_sub` silently accepts releasing more than is reserved. Once the state is inconsistent, a late `sweep_expired` can release units that belong to another hold, which overstates availability. Return an error when `qty > reserved`.

**`confirm` (L260–266) drops the hold before shipping.** The hold is removed from the map before `ship` runs. If `ship` fails, the hold is gone and its units stay reserved forever. Check the shipment first, or reinsert the hold on failure.

## Concurrency

**Lock-order inversion, which can deadlock.** `place_hold` (L245–247) and `sweep_expired` (L272–273) take `warehouse` and then `holds`. `confirm` takes `holds` (L259) and then `warehouse` (L262, L265). Thread A can hold `warehouse` while waiting for `holds`, and thread B can hold `holds` while waiting for `warehouse`. The simplest fix is one `Mutex` around a state struct containing the warehouse, the holds, and the id counter. That removes the ordering problem and makes `sweep_expired` and `confirm` atomic with respect to each other.

**Poisoning cascades.** Every `lock().unwrap()` turns one panic while a lock is held into a permanent failure of the service. Combined with the `record_loss` panic above, a single bad loss record can take the whole service down. Fixing the panics removes most of the exposure, but consider `lock().unwrap_or_else(|e| e.into_inner())` if you want the service to survive a poisoned lock.

## Tests

The two existing tests and `parse_ok` cover only the happy path. None of the defects above would be caught. Add tests for `receive` onto an existing SKU, `deltas` on a multi-element slice, `decode` with invalid UTF-8, `lookup` out of range, `record_loss` beyond stock, and `encode` with a 300-byte name.

ISSUES:
L47: available() underflows when reserved exceeds on_hand, which wraps in release and allows overselling
L81: receive() replaces the existing item, clobbering on_hand, reserved, name and price instead of adding stock
L101: release() saturates silently, hiding over-release and letting one hold's release free another hold's units
L120: record_loss() does not check lost against stock, so it panics or wraps on_hand
L127: total_value() can overflow u64 in the multiplication and the sum
L157: deltas() indexes prices[i + 1] past the end on the last iteration, so it panics on any non-empty input
L185: lookup() uses get_unchecked with an untrusted scanner index, which is an out-of-bounds read (UB)
L196: append_batch() dereferences a pointer into buf that dangles after extend_from_slice reallocates (UB)
L204: encode() truncates name length to u8, producing corrupt records for names over 255 bytes
L218: decode() uses from_utf8_unchecked on untrusted network bytes (UB on invalid UTF-8)
L245: lock().unwrap() on warehouse makes a panic under lock permanently break the service (poisoning)
L253: Instant::now() + ttl panics on overflow for large caller-supplied TTLs
L259: confirm() takes holds then warehouse, inverting the warehouse-then-holds order used elsewhere (deadlock)
L266: confirm() removes the hold before ship() succeeds, so a failed ship leaks the reservation