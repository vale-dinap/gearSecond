The module has undefined behavior on three unchecked paths, a lock-order deadlock in `Service`, and inventory arithmetic that panics in debug builds and wraps in release builds.

### Memory safety

`SlotTable::lookup` (L185) calls `get_unchecked` on a slot index the comment says comes from a scanner. If `slot >= slots.len()`, that read is undefined behavior.

`append_batch` (L194–L196) takes a raw pointer at the current end of `buf`, then calls `extend_from_slice`. That can reallocate and free the old buffer. The `unsafe` read of `first` is then a use-after-free. The value it wants is already in `head`.

`decode` (L218) runs `from_utf8_unchecked` on bytes the comment says arrived from the network. If those bytes are not UTF-8, constructing a `&str` is undefined behavior. The following `try_into().unwrap()` calls are safe: the length check guarantees those slices are 4 bytes.

### Panics and overflow

In debug builds, overflowing integer arithmetic panics. In release builds it wraps, so quantities and money silently corrupt.

- `Item::available` (L47) does `on_hand - reserved`. Any path that leaves `reserved > on_hand` panics here, including `reserve` and `low_stock`.
- `record_loss` (L120) does `on_hand -= lost` with no check against `on_hand` or `reserved`. A loss larger than `on_hand` underflows, and a smaller loss can still push `on_hand` below `reserved`.
- `ship` (L112) checks `reserved` only. After that invariant is broken, `on_hand -= qty` underflows. `reserved` is already reduced by then, so a panic also leaves the row half-updated.
- `total_value` (L127) can overflow both on `on_hand as u64 * price_cents` and on the `sum()`.
- `deltas` (L156) walks `0..prices.len()` and reads `prices[i + 1]`. For every non-empty slice the last step is out of bounds and panics. An empty slice returns an empty vec. The subtraction (L157) can also overflow `i64` (`i64::MIN - 1`, `i64::MAX - (-1)`).
- `moving_average` (L144) `assert!`s and panics when `window == 0`.
- `next_id` (L250) uses `+= 1`. At `u64::MAX` that panics in debug, or wraps to 0 in release and `HashMap::insert` overwrites an existing hold, leaving its units reserved with no entry.
- `Instant::now() + ttl` (L253) panics if the deadline is not representable. `reserve` has already succeeded, so those units stay reserved and no hold is stored.

### Logic

`receive` (L81) always `insert`s a new `Item` whose `on_hand` is `qty` and whose `reserved` is 0. For an existing SKU this drops the previous on-hand quantity, clears reservations, and replaces the name and price. The doc comment describes adding units to the existing row. Outstanding `Service` holds still refer to the old reservation.

`release` (L101) uses `saturating_sub` and returns `Ok(())` when `qty` is greater than `reserved`. The reservation count shrinks by less than the caller asked, and the caller is told it succeeded. `reserve` and `ship` both report `Insufficient` for the same kind of mismatch.

`encode` (L204) stores `name.len() as u8`. A name longer than 255 bytes is truncated in the length prefix, so `decode` treats later name bytes as the SKU and quantity.

`confirm` (L260) `remove`s the hold before `release` or `ship` has succeeded. If `ship` returns `Insufficient`, the hold is already gone, the units stay in `reserved`, and `sweep_expired` will never see them. The same removal happens before the expired-path `release`, so an error there drops the hold without returning the stock.

### Concurrency

`place_hold` locks `warehouse` and then `holds` (L245, L247). `sweep_expired` uses that same order (L272, L273). `confirm` locks `holds` and then `warehouse` (L259, then L262 or L265). Two threads, one in `confirm` and one in `place_hold` or `sweep_expired`, can each hold one mutex and wait for the other. That deadlock is permanent. `place_hold` may already have reserved the stock.

ISSUES:
L47: available() underflows when reserved > on_hand (debug panic, release wrap)
L81: receive() replaces an existing SKU, resetting on_hand to qty and reserved to 0
L101: release() saturates and returns Ok when qty exceeds reserved
L112: ship() subtracts qty from on_hand without an on_hand check and can underflow
L120: record_loss() subtracts lost from on_hand unchecked and can leave reserved above on_hand
L127: total_value() product and sum can overflow u64
L144: moving_average() panics when window is 0
L156: deltas() indexes prices[i + 1] for every i including the last, panicking on a non-empty slice
L157: deltas() i64 subtraction can overflow
L185: lookup() get_unchecked on an untrusted slot is undefined behavior when out of range
L196: append_batch() dereferences a buf pointer after extend_from_slice may reallocate (use-after-free)
L204: encode() truncates name.len() to u8, corrupting names longer than 255 bytes
L218: decode() from_utf8_unchecked on network bytes is undefined behavior for invalid UTF-8
L250: next_id += 1 overflows u64, panicking or overwriting an existing hold id
L253: Instant::now() + ttl panics on overflow after reserve has already succeeded
L259: confirm() locks holds then warehouse, deadlocking with place_hold and sweep_expired
L260: confirm() removes the hold before ship/release commits, leaking the reservation on failure