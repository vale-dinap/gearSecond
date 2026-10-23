I'll review the inventory module for logic errors, panics, overflow, undefined behavior, and concurrency bugs, and check the source so the line numbers match.The workspace listing was empty, so I am checking whether `src/lib.rs` is present before relying on the pasted line numbers.The module can corrupt stock counts, panic on ordinary inputs, hit undefined behavior on untrusted data, and deadlock when two calls run together. Unchecked `u32`, `u64`, and `i64` arithmetic panics in debug builds and wraps in release builds.

### Inventory accounting

`receive` always builds a new `Item` with `on_hand: qty` and `reserved: 0`, then `insert`s it. For a SKU that is already present, that drops the previous row. The method comment says a second receipt adds `qty` to the units already on hand. After `receive(1, "bolt", 10, 25)` and `reserve(1, 4)`, another `receive(1, "bolt", 5, 25)` leaves `on_hand == 5` and `reserved == 0`.

`release` uses `saturating_sub` and returns `Ok(())` when `qty` is larger than `reserved`. An oversized release therefore succeeds and can wipe reserved units that belong to other holds on that SKU. With two holds of 5 (`reserved == 10`), `release(sku, 6)` leaves `reserved == 4`, and both later ships fail `Insufficient`.

`record_loss` does `on_hand -= lost` with no check against `on_hand` or the reserved quantity. `lost > on_hand` panics in debug and wraps `on_hand` in release. A smaller loss that still eats reserved stock leaves `reserved > on_hand` (10 on hand, 4 reserved, loss of 7 leaves `on_hand == 3` and `reserved == 4`).

`available` is `on_hand - reserved`. Once `reserved > on_hand`, debug builds panic there and release builds wrap to a huge available count, which `reserve` and `low_stock` then trust. `ship` only compares `qty` with `reserved`, then subtracts `qty` from `reserved` and from `on_hand`. If `on_hand < qty`, the second subtraction panics or wraps after `reserved` has already changed, so a panic leaves the row half-updated.

`total_value` computes `on_hand as u64 * price_cents` and sums those products in `u64`. A large quantity times a large price, or many rows together, overflows the accumulator.

### Other panics and overflow

`moving_average` asserts `window > 0` and panics on a zero window. The window total is a `u64`, so a window whose daily counts sum past `u64::MAX` overflows too. That needs more than 2^32 samples if every count is `u32::MAX`.

`deltas` reserves `len - 1` slots but loops `i` over `0..prices.len()`. On every non-empty slice the last step reads `prices[i + 1]`, which is out of bounds and panics in every build mode. An empty slice returns an empty `Vec`. The subtraction `prices[i + 1] - prices[i]` also overflows `i64` on large swings, such as `[i64::MIN, 0]`. In debug that panic happens on the overflowing pair.

`place_hold` sets the deadline with `Instant::now() + ttl`. That addition panics in every build mode when the result does not fit in `Instant`, which `Duration::MAX` triggers. `reserve` has already succeeded, the hold is never inserted, and the panic unwinds while the warehouse and holds mutexes are held, so both poison. Later `lock().unwrap()` calls panic as well, and nothing can release those units because there is no hold.

`next_id` does `*n += 1`. Debug overflow panics in that same window, with the same leaked reservation and poisoned mutexes. In release the counter wraps, and `holds.insert` replaces the hold that already owns that id. The old hold is dropped with no `release`, so its units stay reserved.

### Undefined behavior

`SlotTable::lookup` evaluates `*self.slots.get_unchecked(slot)`. `assign` returns `Malformed` for an index past the end of `slots`. The same index in `lookup` is undefined behavior as soon as the unchecked reference is formed. `slot` is documented as coming straight from a handheld scanner message, so an out-of-range value is a normal input.

`append_batch` stores `buf.as_ptr().wrapping_add(start)` after pushing the first SKU, calls `extend_from_slice` on the tail, then reads through that pointer. If the tail does not fit in the spare capacity, `extend_from_slice` reallocates and the old pointer is invalid. The read is then a use after free. `Vec::with_capacity(1)` and a two-SKU batch is enough: `push` fills the buffer and the extend moves it. The SKU being read is already in `head`.

`decode` builds the name with `std::str::from_utf8_unchecked`. The bytes are a network record. Invalid UTF-8 makes that conversion undefined behavior. The earlier length check only ensures that `len` name bytes and the 8-byte trailer are inside the buffer.

### Wire format

`encode` stores `name.len() as u8`. Lengths above 255 truncate (256 becomes 0) while every name byte is still appended. `decode` trusts that prefix, cuts the name there, and reads the SKU and quantity from the next 8 bytes, which are still name bytes. The real SKU and quantity are further along the buffer and are ignored. Names of 255 bytes or fewer round-trip. The test name is `"nut"`.

### Concurrency

The three mutexes are taken in different orders:

- `place_hold` locks `warehouse`, then `holds`, then `next_id`.
- `sweep_expired` locks `warehouse`, then `holds`.
- `confirm` locks `holds`, then `warehouse`.

`confirm` beside `place_hold` or `sweep_expired` deadlocks. One thread holds `holds` and waits for `warehouse`. The other holds `warehouse` and waits for `holds`. Both stay blocked, and every later call that needs either mutex queues behind them.

`confirm` removes the hold before it locks `warehouse`. On the deadlock path the hold is already gone, its units are still reserved, and the thread that could ship or release them is stuck on `holds`. `ship` is also fallible. Its `Result` is returned after the removal, so `Insufficient` or `UnknownSku` leaves `reserved` unchanged and deletes the only record `sweep_expired` could use to release those units.

ISSUES:
L47: `available` does unchecked `on_hand - reserved`, panicking in debug and wrapping in release when `reserved > on_hand`
L81: `receive` inserts a new row with `on_hand: qty` and `reserved: 0`, dropping any existing stock and reservations for that SKU
L101: `release` saturates and returns `Ok` when `qty` exceeds `reserved`, so an oversized release clears other holds' units
L112: `ship` subtracts `qty` from `on_hand` after checking only `reserved`; `on_hand < qty` panics or wraps after `reserved` is already reduced
L120: `record_loss` does `on_hand -= lost` with no check, panicking or wrapping, and can leave `reserved > on_hand`
L127: `total_value` multiplies and sums in `u64` with no overflow check, panicking in debug and wrapping in release
L144: `moving_average` asserts and panics when `window` is 0
L147: `moving_average` accumulates the window in `u64`, which overflows when the window total exceeds `u64::MAX`
L156: `deltas` loops `0..prices.len()`, so the last step reads `prices[i + 1]` out of bounds and panics on every non-empty slice
L157: `deltas` subtracts `i64` prices with no overflow check, panicking in debug and wrapping in release
L185: `lookup` uses `get_unchecked` on a scanner-supplied slot, which is undefined behavior when the index is out of range
L196: `append_batch` dereferences a pointer into `buf` after `extend_from_slice`, which is undefined behavior if the `Vec` reallocates
L204: `encode` stores `name.len() as u8`, so names longer than 255 bytes truncate the length and corrupt the frame
L218: `decode` uses `from_utf8_unchecked` on network bytes, which is undefined behavior when the name is not UTF-8
L250: `next_id += 1` overflows, panicking in debug after `reserve` or wrapping in release and overwriting an existing hold without releasing it
L253: `Instant::now() + ttl` panics on overflow after `reserve` has committed, leaking the reservation and poisoning the warehouse and holds mutexes
L259: `confirm` locks `holds` then `warehouse`, opposite of `place_hold` and `sweep_expired`, so those pairs deadlock
L260: `confirm` removes the hold before `ship` or `release` finishes, so a failed ship or a deadlock drops the hold and leaves its units reserved