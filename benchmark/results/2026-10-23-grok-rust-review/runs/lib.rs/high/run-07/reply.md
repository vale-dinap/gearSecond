The module has soundness holes, a lock-order deadlock, and several inventory paths that panic, wrap, or drop stock.

### Memory safety

`SlotTable::lookup` (L185) is a safe function that calls `get_unchecked`. A slot index from the scanner that is `>= slots.len()` is undefined behavior. It can crash or return a garbage `Sku`. `assign` bounds-checks; `lookup` does not.

`append_batch` (L194–L196) saves `buf.as_ptr().wrapping_add(start)` and then calls `extend_from_slice`. That extend reallocates whenever the vector is full, which frees the buffer `first` points at. The later `unsafe { *first }` is a use-after-free. A two-SKU batch into an empty or full buffer hits this. `head` was already copied on L191, so the pointer read is unnecessary.

`decode` (L218) runs `str::from_utf8_unchecked` on bytes the comment says came off the network. Invalid UTF-8 is undefined behavior. A safe function must use `str::from_utf8` and return `InvError::Malformed`.

`encode` (L204) stores `name.len() as u8`. A name of 256 bytes or more is still written in full, but the length prefix wraps (256 becomes 0, 300 becomes 44). `decode` then treats the frame as valid and returns the wrong name, SKU, and quantity. If the truncated length splits a multibyte character, the unchecked UTF-8 read is undefined behavior on `encode`'s own output.

### Concurrency

Lock order is not consistent:

- `place_hold` (L245) and `sweep_expired` (L272) take `warehouse`, then `holds`.
- `confirm` (L259) takes `holds`, then `warehouse` (L262 and L265), and it holds `holds` across that second lock.

One thread in `sweep_expired` or `place_hold` can own `warehouse` and wait for `holds` while `confirm` owns `holds` and waits for `warehouse`. Both wait forever. `place_hold` has already called `reserve` at that point, so the stuck thread also holds a reservation that never becomes a hold.

`confirm` (L260) deletes the hold before `release` or `ship`. If either call returns `Err`, the id is gone and the units stay in `reserved` with no hold left to confirm or sweep.

### Panics and overflow

`deltas` (L156) walks `0..prices.len()` and reads `prices[i + 1]`. For every non-empty slice the last step is out of bounds and panics in both debug and release. An empty slice happens to return an empty vec. The `saturating_sub(1)` capacity on L155 is the bound the loop should have used.

The subtraction on L157 uses wrapping `i64` arithmetic. `i64::MAX - i64::MIN` panics in debug and wraps in release, so a fixed loop bound still overflows.

`Item::available` (L47) is `on_hand - reserved`. If `reserved > on_hand`, debug builds panic and release builds wrap to a huge `u32`. `reserve` and `low_stock` both call it, so a wrapped result lets `reserve` accept a quantity the shelf does not have. `reserved += qty` (L95) can then overflow too.

`record_loss` (L120) does `on_hand -= lost` with no check. `lost > on_hand` panics in debug and wraps in release. A smaller loss that still exceeds the unreserved quantity leaves `reserved > on_hand`, which is what blows up `available` and `ship`.

`ship` (L112) only checks `qty <= reserved`, then does `on_hand -= qty`. Once `record_loss` has broken `on_hand >= reserved`, a legal ship quantity panics or wraps.

`total_value` (L127) does `on_hand as u64 * price_cents` and sums in `u64`. Two units at a price above `u64::MAX / 2` panics in debug and wraps in release, so the reported value is wrong.

`place_hold` (L253) computes `Instant::now() + ttl`. `Instant + Duration` panics if the instant overflows (`Duration::MAX` does this). `reserve` has already run, and the hold is inserted only after the addition, so a panic leaves stock reserved with no hold. The `warehouse` guard is still alive, which poisons that mutex; later `lock().unwrap()` calls panic as well.

### Inventory logic

`receive` (L80–L81) does not add to an existing SKU. It builds a new `Item` with `on_hand: qty` and `reserved: 0` and `insert`s it, which drops the previous record. A second receipt replaces stock instead of increasing it, clears outstanding reservations, and desynchronizes any `Hold`s for that SKU. The comment on L77–L78 says existing units are added.

`release` (L101) uses `saturating_sub` and returns `Ok(())` when `qty > reserved`. `reserve` and `ship` return `Insufficient` for the same kind of mismatch. An over-release reports success and clamps the shared per-SKU counter to zero, which drops reservations that belong to other holds. A later `ship` of those holds then fails `qty > reserved`.

ISSUES:
L47: available() does on_hand - reserved unchecked, so reserved > on_hand panics in debug or wraps in release
L81: receive() replaces an existing SKU instead of adding qty, and resets reserved to 0
L101: release() saturates and returns Ok when qty > reserved, clearing other reservations
L112: ship() subtracts qty from on_hand without checking on_hand, so it panics or wraps when on_hand < qty
L120: record_loss() does on_hand -= lost unchecked; it panics or wraps and can leave reserved > on_hand
L127: total_value() multiplies and sums in u64, which panics in debug and wraps in release on overflow
L156: deltas() iterates 0..len, so the last iteration reads prices[len] and panics
L157: deltas() subtracts i64 with the built-in operator, which overflows (debug panic, release wrap)
L185: lookup() uses get_unchecked on a scanner index; an out-of-range slot is undefined behavior
L196: append_batch() dereferences a pointer after extend_from_slice, which can reallocate and free it (use-after-free)
L204: encode() stores name.len() as u8, so names longer than 255 bytes get a truncated length and decode reads the wrong fields
L218: decode() uses from_utf8_unchecked on network bytes; invalid UTF-8 is undefined behavior
L253: Instant::now() + ttl panics on overflow after reserve(), so stock stays reserved, no hold is stored, and the warehouse mutex is poisoned
L259: confirm() locks holds then warehouse while place_hold() and sweep_expired() lock warehouse then holds, which deadlocks
L260: confirm() removes the hold before release()/ship(); a failure leaves the units reserved with no hold to retry