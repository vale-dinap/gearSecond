I'll review the module for logic errors, panics, overflow, undefined behaviour, and concurrency bugs, and check the source so the line numbers match.The module has merge-blocking defects in stock accounting, several panics and integer overflows, three unsound `unsafe` blocks, a codec that corrupts long names, and a lock-order deadlock in `Service`.

### Stock accounting

`receive` always `insert`s a fresh `Item` whose `on_hand` is only the new `qty`. The comment requires a new SKU to be created with the given name and price, and an existing SKU to gain `qty` on top of the units already on hand. A second receipt discards the previous `on_hand`, the outstanding `reserved` count, the name, and the price. Reservations and holds that still refer to the old `reserved` value are left pointing at stock the map no longer tracks.

`available` computes `on_hand - reserved` with plain `u32` subtraction. That underflows whenever `reserved > on_hand`: debug builds panic, release builds wrap. Both fields are public, so any caller can construct that state. `record_loss` creates it on its own. `on_hand -= lost` is unchecked. If `lost > on_hand`, debug panics and release wraps `on_hand` to a huge value. A smaller loss that still cuts into reserved units succeeds and leaves `reserved > on_hand` (10 on hand, 8 reserved, lose 5 → 5 on hand and 8 reserved). The next `available`, `reserve`, or `low_stock` call then panics or wraps. In release, the wrapped `available()` is a huge `u32`, so `reserve`'s `qty > have` check passes and `reserved += qty` can overflow as well.

`ship` checks `qty` only against `reserved`, then does `reserved -= qty` and `on_hand -= qty`. Once `reserved > on_hand`, the `on_hand` update panics in debug or wraps in release. `reserved` has already been reduced if that panic is caught.

`release` never returns `Insufficient`. `saturating_sub` clamps `reserved` at 0 and the function returns `Ok(())`. A release larger than the reserved quantity reports success, and the caller's count no longer matches the warehouse. `reserve` and `ship` both reject an oversized quantity.

`total_value` multiplies `on_hand as u64 * price_cents` and sums the products with `+`. `price_cents` is already a `u64`, so one expensive SKU, or several moderate ones, can exceed `u64::MAX`. Debug builds panic. Release builds wrap and report a total that is far too small.

### `deltas` and `moving_average`

`deltas` iterates `for i in 0..prices.len()` and evaluates `prices[i + 1] - prices[i]`. The last step always reads one past the end. Every non-empty slice panics, in debug and in release. The `with_capacity(len - 1)` hint is the length the function would have if the loop stopped one earlier. Pairs that are in range can also overflow `i64` (`i64::MAX - (-1)`, or any swing that does not fit). Debug panics on that subtraction. Release wraps, then the trailing out-of-bounds read panics anyway, so the function never returns a value for a non-empty input.

`moving_average` hits `assert!(window > 0)` and panics on a zero window. The window sum is a `u64`. It overflows when the samples in the window add up past `u64::MAX` (on the order of `2^32` values at `u32::MAX`). Debug panics; release wraps the average.

### Undefined behaviour

`SlotTable::lookup` takes a slot from a handheld scanner message and calls `slots.get_unchecked(slot)`. `get_unchecked` is undefined behaviour when `slot >= slots.len()`. `assign` bounds-checks and returns `Malformed`. An in-range empty slot yields `None`. An out-of-range slot is undefined behaviour, which can surface as a crash or as a garbage `Sku`.

`append_batch` saves `buf.as_ptr().wrapping_add(start)` after pushing the first SKU, calls `extend_from_slice` on the tail, then reads that pointer. `extend_from_slice` reallocates whenever `tail` does not fit in the spare capacity, frees the old buffer, and leaves `first` dangling. The read is a use-after-free. The first SKU is already in `head`, so the pointer round-trip is what makes the function unsound. A one-element batch often avoids reallocation and hides it.

`decode` builds the name with `std::str::from_utf8_unchecked` on bytes received from the network. Invalid UTF-8 makes that undefined behaviour, and the resulting `String` breaks the UTF-8 invariant the rest of the standard library assumes. Invalid input should return `InvError::Malformed`. The `len + 8` check is sufficient for the following SKU and quantity slices, so those `try_into().unwrap()` calls do not panic.

### Codec

`encode` stores `name.len() as u8`. A name longer than 255 bytes is truncated in the length prefix (300 becomes 44) while the full byte string is still appended. `decode` then treats part of the name as the SKU and quantity, or rejects the frame as short. A round trip changes the identity of the record. Names that do not fit in a `u8` need to be rejected, or the length field needs to be wider.

### Concurrency

`Service` takes its mutexes in two orders.

- `place_hold` and `sweep_expired` lock `warehouse`, then `holds`.
- `confirm` locks `holds`, then `warehouse`, both on the expired `release` path and on the `ship` path.

One thread in `confirm` and another in `place_hold` or `sweep_expired` can each hold the mutex the other is waiting on and hang with no timeout.

`place_hold` computes `Instant::now() + ttl` after `reserve` has succeeded, while the warehouse and holds locks are still held. `Instant + Duration` panics when the deadline cannot be represented, which `Duration::MAX` and any very large TTL will do. The `Hold` is never inserted, so those units stay reserved with no id that can confirm or sweep them. Unwinding drops both guards and poisons both mutexes. Every later `lock().unwrap()` panics, so one oversized TTL wedges the whole service.

`parse_command` matches its checks. The three tests cover one reserve/ship, a short ASCII name, and a single parse, so none of these paths run.