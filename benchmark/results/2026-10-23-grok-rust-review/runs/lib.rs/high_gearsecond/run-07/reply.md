I'll review the inventory module for logic errors, panics, overflow, and memory-safety or concurrency bugs.This module has memory-safety undefined behavior, a lock-order deadlock, debug-panic overflows, and inventory updates that drop or leak stock.

### Memory safety

`SlotTable::lookup` (L185) reads `self.slots` with `get_unchecked`. A `slot` past the end of the table is undefined behavior. The index comes from a scanner message and is not checked first.

`append_batch` (L194–L196) takes a pointer at index `start`, then calls `extend_from_slice`. That can reallocate and free the buffer. The later `*first` is a use-after-free. A one-element batch often avoids the realloc; any batch longer than the spare capacity hits it.

`decode` (L218) builds a `String` with `from_utf8_unchecked` on bytes from the network. Invalid UTF-8 is undefined behavior. The length check above it only guarantees that eight bytes follow the name; it says nothing about UTF-8.

### Panics and overflow

`Item::available` (L47) does `on_hand - reserved`. `Item`'s fields are public, and `record_loss` can make `reserved > on_hand`. The subtraction panics in debug and wraps in release. `reserve` and `low_stock` both call `available`, so they panic on the same state.

`record_loss` (L120) does `on_hand -= lost` with no check against `on_hand`. `lost` larger than `on_hand` underflows the same way, and it leaves `reserved` above `on_hand`.

`ship` (L112) checks `qty` against `reserved` only. `on_hand -= qty` still underflows when `reserved` is higher than `on_hand`.

`total_value` (L127) does `on_hand as u64 * price_cents` and then sums those products in `u64`. Either the multiply or the sum panics in debug and wraps in release.

`deltas` (L157) loops `i` over `0..prices.len()` and reads `prices[i + 1]`. On every non-empty slice the last step is `prices[len]`, which panics. Earlier steps can also overflow: `i64` subtraction panics in debug and wraps in release (`i64::MIN - i64::MAX`). The `saturating_sub(1)` on the capacity hint is the bound the loop should have used. An empty slice returns an empty `Vec`; a one-element slice panics.

`moving_average` (L144) `assert`s and panics when `window` is 0.

`place_hold` (L253) evaluates `Instant::now() + ttl` after `reserve` has already succeeded. A large `ttl` (`Duration::MAX` is enough) panics. The hold is never inserted, the units stay reserved, and the panic poisons both the warehouse and holds mutexes. Later `lock().unwrap()` calls then panic as well.

### Inventory logic

`receive` (L81) inserts a brand-new `Item` whose `on_hand` is only `qty` and whose `reserved` is 0. For an existing SKU that replaces the previous record: prior units, live reservations, the old name, and the old price are gone. The comment says the units are added to what is already on hand.

`release` (L101) uses `saturating_sub` and returns `Ok(())` when `qty` is greater than `reserved`. Releasing 100 against a reservation of 5 sets `reserved` to 0 and reports success. A later `confirm` of that hold then fails `ship`, and those units are free to sell again.

`confirm` (L260) `remove`s the hold before `ship` (L266) or the expiry `release` (L262). If `ship` returns `Insufficient`, the id is gone and the units that are still reserved have no hold left. `sweep_expired` will not see them, so they stay reserved.

`encode` (L204) stores `name.len() as u8`. A name longer than 255 bytes writes a truncated length and then the full byte string. `decode` treats the next bytes of the name as the SKU and quantity.

### Concurrency

The mutex order is not consistent:

- `place_hold` locks warehouse (L245), then holds (L247).
- `sweep_expired` locks warehouse (L272), then holds (L273).
- `confirm` locks holds (L259), then warehouse (L262 or L265), while the holds guard is still alive.

One thread in `confirm` can hold `holds` and wait for `warehouse` while another thread in `place_hold` or `sweep_expired` holds `warehouse` and waits for `holds`. That is a deadlock. A `place_hold` stuck there has already called `reserve` and has not inserted the hold, so those units stay reserved for as long as the threads stay blocked.

ISSUES:
L47: available() underflows when reserved exceeds on_hand
L81: receive() replaces an existing SKU, wiping stock and reservations
L101: release() saturates and returns Ok when qty exceeds reserved
L112: ship() subtracts from on_hand without checking on_hand and can underflow
L120: record_loss() subtracts lost from on_hand with no bounds check
L127: total_value() multiplies and sums in u64 and can overflow
L144: moving_average() panics when window is 0
L157: deltas() reads prices[i + 1] on the last index and panics for every non-empty slice
L157: deltas() subtracts i64 values with no overflow check
L185: lookup() uses get_unchecked, which is undefined behavior when slot is out of range
L196: append_batch() dereferences a pointer into buf after extend_from_slice can reallocate it
L204: encode() truncates name.len() to u8, so names longer than 255 bytes encode the wrong length
L218: decode() uses from_utf8_unchecked on network bytes; invalid UTF-8 is undefined behavior
L253: Instant::now() + ttl panics on overflow after reserve(), leaking the reservation and poisoning both mutexes
L260: confirm() removes the hold before ship() succeeds, so a failed ship leaks the reservation
L262: confirm() locks warehouse while holding holds, opposite of place_hold and sweep_expired, so those calls deadlock