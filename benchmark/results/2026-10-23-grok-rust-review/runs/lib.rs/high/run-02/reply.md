This module has undefined behavior in three safe functions, debug panics and integer overflows on stock and price math, inventory updates that drop or double-allocate units, and a lock-order deadlock in `Service`.

### Memory safety

`SlotTable::lookup` (line 185) takes `slot` straight from a scanner message and calls `get_unchecked`. If `slot >= slots.len()`, including every lookup on an empty table, that is undefined behavior. The `unsafe` block sits inside a safe function, so callers can hit it with ordinary code. `assign` is bounds-checked; `lookup` is not.

`append_batch` (lines 194–196) saves `buf.as_ptr().wrapping_add(start)` and then calls `extend_from_slice(tail)`. `extend_from_slice` reallocates when the spare capacity is smaller than `tail`, which is what happens for any multi-SKU batch once `push` has filled the buffer. Reallocation frees the old allocation, and `*first` is a use-after-free. The first SKU is already in `head`; the pointer round-trip is what makes this undefined behavior.

`decode` (line 218) turns network bytes into a `String` with `str::from_utf8_unchecked`. Invalid UTF-8 is undefined behavior. The `Result` does not report it. Combined with the truncated length prefix below, a long name this crate encoded can split a multibyte character and trip the same unchecked conversion.

### Panics and overflow

`deltas` (lines 156–157) only works for an empty slice. The loop is `for i in 0..prices.len()` and the body reads `prices[i + 1]`. On a slice of length `n > 0` the last `i` is `n - 1`, so `prices[n]` panics. `deltas(&[10, 12, 15])` panics; the `Vec` capacity of `len - 1` is the count the loop should have produced. Earlier iterations also do a raw `i64` subtraction. `deltas(&[-1, i64::MAX])` overflows `i64::MAX - (-1)`, which panics in debug and wraps in release.

`Item::available` (line 47) is `on_hand - reserved`. When `reserved > on_hand` that panics in debug and wraps in release. `reserve` and `low_stock` both call it. In release the wrapped available count is huge, so `reserve` accepts the request and `reserved += qty` can overflow too. `on_hand` and `reserved` are public, so callers can break the invariant directly.

`record_loss` (line 120) does `on_hand -= lost` with no check against `on_hand` or against unreserved stock. `lost > on_hand` panics or wraps. A smaller loss still leaves `reserved > on_hand` (10 on hand, 8 reserved, lose 5 → 5 on hand and 8 reserved). `available`, `low_stock`, and `ship` then see a broken item. Those lost units are still reserved and can later be “shipped.”

`ship` (line 112) checks `qty > reserved` and then does `on_hand -= qty`. Once `on_hand < reserved`, shipping units that are still reserved underflows `on_hand`: panic in debug, wrap to a huge stock count in release.

`total_value` (line 127) computes `on_hand as u64 * price_cents` and sums the products in `u64`. The multiply or the sum panics in debug and wraps in release. One SKU with `on_hand = 3_000_000_000` and `price_cents = 10_000_000_000` overflows the product.

`place_hold` (line 253) evaluates `Instant::now() + ttl` after `reserve` has succeeded. A `ttl` that does not fit in `Instant` (for example `Duration::MAX`) panics. The `Hold` is never inserted, the units stay reserved, and unwinding poisons the `warehouse` and `holds` mutexes. Later `lock().unwrap()` calls panic as well.

`moving_average` asserts `window > 0`. That matches the stated precondition. The window sum is a `u64` and overflows only for a window of about 2^32 maximum-sized samples.

### Inventory logic

`receive` (lines 80–81) always `insert`s a new `Item` with `on_hand: qty` and `reserved: 0`. The comment says an existing SKU gains `qty` units. A second receipt replaces the previous balance and clears reservations. Those units become available again while any `Hold`s for that SKU are still live, so the same stock can be reserved twice. The next `confirm` then fails `ship` because `reserved` was zeroed.

`release` (line 101) uses `saturating_sub` and returns `Ok` when `qty` is above `reserved`. Reservations for one SKU share a single counter. Releasing more than one hold’s quantity clears the others too. Those units look available and can be reserved again while the old holds remain. `ship` reports this case as `Insufficient`; `release` does not.

`confirm` (line 260) `remove`s the hold before `release` or `ship`. Both return `Result`, and `?` returns immediately on error. The id is gone, so the caller cannot retry and `sweep_expired` will not see it. If `ship` returns `Insufficient`, the units stay in `reserved` with no hold left. `sweep_expired` (line 278) drops the hold even when the `release` result is discarded.

### Concurrency

`Service` uses three mutexes and two lock orders. `place_hold` (line 245) and `sweep_expired` (line 272) take `warehouse`, then `holds`. `confirm` (line 259) takes `holds`, then `warehouse`, and it keeps `holds` for the whole warehouse call. `std::sync::Mutex` does not recover from that cycle: one thread in `confirm` holding `holds` and waiting for `warehouse`, and another in `place_hold` or `sweep_expired` holding `warehouse` and waiting for `holds`, block forever. `place_hold` has already reserved the stock before it waits, so the deadlocked call also strands units with no map entry. `next_id` is only locked from `place_hold` and is not part of the cycle.

The existing tests cover one reserve/ship path, a short ASCII codec round trip, and a valid parse. They do not exercise these paths.

ISSUES:
L47: `available` computes `on_hand - reserved`, panicking in debug and wrapping in release when `reserved > on_hand`
L81: `receive` inserts a new item with `on_hand = qty` and `reserved = 0`, replacing an existing SKU instead of adding quantity
L101: `release` saturates `reserved` to zero and returns Ok when `qty` exceeds `reserved`, clearing every reservation on that SKU
L112: `ship` subtracts `qty` from `on_hand` after checking only `reserved`, so `on_hand` underflows when it is below `qty`
L120: `record_loss` does `on_hand -= lost` with no bounds check, panicking or wrapping and leaving `reserved` above `on_hand`
L127: `total_value` multiplies `on_hand` by `price_cents` and sums in `u64`, overflowing on large stock values
L156: `deltas` iterates `i` over `0..prices.len()` and reads `prices[i + 1]`, panicking out of bounds for every non-empty slice
L157: `deltas` subtracts `i64` prices directly, so large swings overflow (panic in debug, wrap in release)
L185: `lookup` uses `get_unchecked` on a scanner-supplied slot; an out-of-range index is undefined behavior
L196: `append_batch` dereferences a raw pointer into `buf` after `extend_from_slice`, which can reallocate and free that pointer (use-after-free, undefined behavior)
L204: `encode` stores `name.len() as u8`, truncating lengths above 255 and emitting a frame `decode` will misread
L218: `decode` builds the name with `from_utf8_unchecked`; invalid UTF-8 from the network is undefined behavior
L253: `place_hold` adds `ttl` to `Instant::now()` after `reserve`, and that addition panics when the deadline overflows
L259: `confirm` locks `holds` then `warehouse`, while `place_hold` and `sweep_expired` lock `warehouse` then `holds`, so concurrent calls deadlock
L260: `confirm` removes the hold before `release` or `ship` succeeds, so an error leaves reserved units with no hold id