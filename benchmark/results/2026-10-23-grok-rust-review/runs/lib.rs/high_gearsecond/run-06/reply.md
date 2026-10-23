This module has three safe functions that can trigger undefined behavior, several arithmetic paths that panic in debug and wrap in release, stock updates that drop or double-sell units, and a lock-order deadlock in `Service`.

### Undefined behavior

`SlotTable::lookup` calls `get_unchecked` on a slot index that comes from a scanner message. If `slot >= slots.len()`, that read is undefined behavior. The method is safe, so callers can hit this with ordinary Rust.

`append_batch` takes a raw pointer at the element just pushed, then calls `extend_from_slice`. When `buf.len() + tail.len() > buf.capacity()`, the extend reallocates and frees that buffer. `unsafe { *first }` is then a use-after-free. `head` already holds the value; the pointer reload is what makes the function unsound. A `Vec` filled to capacity plus a multi-SKU batch reallocates.

`decode` turns network bytes into a `String` with `from_utf8_unchecked`. Any non-UTF-8 name is undefined behavior. A truncated length prefix can also split a multibyte character on a round trip and hit the same path.

### Panics and overflow

`deltas` walks `0..prices.len()` and reads `prices[i + 1]`. Every non-empty slice panics on the last step. An empty slice returns an empty `Vec`. The subtraction can also overflow `i64` (`0 - i64::MIN` is enough): debug panic, release wrap.

`Item::available` computes `on_hand - reserved` with no check. Debug builds panic when `reserved > on_hand`. Release builds wrap, and `reserve` then treats that wrapped value as free stock.

`record_loss` does `on_hand -= lost` with no check against `on_hand` or `available`. `lost > on_hand` panics or wraps. A smaller loss still breaks the invariant: receive 10, reserve 8, lose 5 leaves `on_hand == 5` and `reserved == 8`. `available` then panics or wraps.

`ship` checks `qty` only against `reserved`, then does `on_hand -= qty`. In that state, `ship(sku, 8)` panics or wraps.

`total_value` multiplies `on_hand as u64 * price_cents` and sums with plain `u64` addition. Either step overflows: debug panic, release wrap, so the reported value is wrong. A price above `u64::MAX / on_hand` is enough.

`moving_average` hits `assert!(window > 0)` and aborts the process. A zero window never returns a `Result`.

`place_hold` evaluates `Instant::now() + ttl` after `reserve` has already succeeded, while both the warehouse mutex and the holds mutex are held. `Instant + Duration` panics when the timestamp does not fit. That poisons both mutexes, so later `lock().unwrap()` panics, and `qty` stays reserved with no hold row, so those units never return to available stock.

### Logic

`receive` is documented to add `qty` to an existing SKU. `HashMap::insert` replaces the row: previous `on_hand` is discarded, `reserved` is cleared, and the name and price are overwritten. A second receipt deletes stock and drops live reservations.

`release` uses `saturating_sub` and returns `Ok(())` when `qty` is greater than `reserved`. The extra units were never reserved, the reservation is cleared, and the same units can be reserved again.

`encode` stores `name.len() as u8`. A name longer than 255 bytes is written in full, but the frame advertises a truncated length. `decode` then reads the SKU and quantity from inside the name.

### Concurrency

`place_hold` locks `warehouse` and then `holds`. `sweep_expired` uses that same order. `confirm` locks `holds` and then `warehouse`, and it keeps the holds lock across `release` and `ship`. One thread in `confirm` and another in `place_hold` or `sweep_expired` deadlock.

`confirm` also `remove`s the hold before `ship` or `release`. A panic inside `ship` (the `on_hand` underflow above) leaves the hold gone and the mutexes poisoned.

The tests cover a single-threaded reserve/ship, a short ASCII codec round trip, and one valid command line.

ISSUES:
L47: available() subtracts reserved from on_hand unchecked (debug panic, release wrap, then over-reserve)
L81: receive() replaces an existing SKU via insert, discarding on_hand and reserved instead of adding qty
L101: release() saturates and returns Ok when qty exceeds reserved, so stock can be reserved twice
L112: ship() checks qty only against reserved, then on_hand -= qty panics or wraps when on_hand < qty
L120: record_loss() does on_hand -= lost with no bounds check (panic/wrap) and can leave reserved > on_hand
L127: total_value() multiplies and sums u64 with no overflow check (debug panic, release wrap)
L144: moving_average() asserts and panics when window is 0
L157: deltas() reads prices[i + 1] for i in 0..len, so every non-empty slice panics out of bounds
L157: deltas() subtracts i64 values with unchecked overflow (debug panic, release wrap)
L185: lookup() uses get_unchecked on a scanner-supplied index (out-of-bounds UB in a safe function)
L196: append_batch() dereferences a buf pointer after extend_from_slice can reallocate (use-after-free UB)
L204: encode() truncates name.len() to u8, so names longer than 255 bytes are framed incorrectly
L218: decode() uses from_utf8_unchecked on network bytes (invalid UTF-8 is UB)
L253: place_hold() panics on Instant::now() + ttl overflow after reserve(), poisoning both mutexes and leaking the reservation
L259: confirm() locks holds then warehouse while place_hold() and sweep_expired() lock warehouse then holds (deadlock)