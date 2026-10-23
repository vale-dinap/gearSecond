This module panics, overflows, hits undefined behavior, deadlocks, and can leave stock reserved with no hold left to release it. The three tests stay on the happy path and miss these cases.

### Stock accounting

`receive` always `insert`s a brand-new `Item`. When the SKU already exists, the previous on-hand count, reservations, name, and price are discarded. The comment says an existing SKU should only gain `qty` units. Any `Hold` for that SKU then disagrees with `reserved`.

`record_loss` does `on_hand -= lost` with no check against `on_hand` or `reserved`. With the default overflow checks that panics in debug when `lost > on_hand`, and wraps in release. A smaller loss that still eats into reserved units leaves `reserved > on_hand`. `Item`'s fields are public, so the same state can be built without calling `record_loss`.

`available` is `on_hand - reserved`. Once `reserved` is larger, that subtraction panics in debug and wraps in release. `reserve` and `low_stock` both call it. In release the wrapped available count is huge, so `reserve` can accept a `qty` that then overflows `reserved += qty`.

`ship` rejects a `qty` above `reserved`, then still does `on_hand -= qty`. That second subtraction overflows when `on_hand < qty <= reserved`. `reserved` is reduced first, so a debug panic on the `on_hand` line leaves `reserved` already changed.

`release` uses `saturating_sub` and returns `Ok(())` when `qty` is above `reserved`. The caller is told the full release worked. The clamp also wipes reserved units that belong to other holds.

`total_value` does `on_hand as u64 * price_cents` and sums the products in `u64`. A high price, or several valuable SKUs, overflows that multiply or the sum: panic in debug, wrap in release.

### `deltas` and `moving_average`

`deltas` loops `for i in 0..prices.len()` and reads `prices[i + 1] - prices[i]`. On a non-empty slice the last index is `len - 1`, so `prices[i + 1]` is out of bounds and panics in debug and release. An empty slice returns an empty `Vec`. The `i64` subtraction also overflows for values such as `i64::MIN - 1` (debug panic, release wrap). `with_capacity(len.saturating_sub(1))` is sized for one fewer element than the loop tries to push.

`moving_average` hits `assert!(window > 0)` and panics when `window` is 0. A positive window longer than the slice yields an empty `Vec`.

### Unsafe code and the codec

`SlotTable::lookup` uses `get_unchecked`. The comment says `slot` comes straight from a scanner message. `slot >= slots.len()` is undefined behavior in debug and release. `get_unchecked` does not insert a debug bounds check.

`append_batch` saves `buf.as_ptr().wrapping_add(start)` and then calls `extend_from_slice`. `Vec::as_ptr` forbids using that pointer after the `Vec` is mutated. `extend_from_slice` may reallocate, and the later `*first` is then a use-after-free. The function already has `head` as a copied `Sku`.

`encode` stores `name.len() as u8`. A name of 256 bytes or more writes a truncated length and then the full name. `decode` trusts that byte. A 256-byte name is stored with length 0, so `decode` returns an empty name and reads the SKU and quantity from the name bytes, and still returns `Ok`.

`decode` builds the name with `from_utf8_unchecked` on bytes the comment says came from the network. Invalid UTF-8 is undefined behavior. The `try_into().unwrap()` calls sit behind a length check, so those unwraps are not the bug. There is no UTF-8 check.

### `Service`

Lock order is inconsistent:

- `place_hold`: `warehouse`, then `holds`, then `next_id` (warehouse is still held)
- `sweep_expired`: `warehouse`, then `holds`
- `confirm`: `holds`, then `warehouse` (both the expiry path and the ship path)

`confirm` deadlocks with `place_hold` when one thread holds `warehouse` and waits for `holds` while the other holds `holds` and waits for `warehouse`. `confirm` deadlocks with `sweep_expired` the same way. Every `lock().unwrap()` panics if that mutex is poisoned, which is what a panic on another thread leaves behind.

`place_hold` reserves stock and only then inserts the `Hold`. `Instant::now() + ttl` panics when the deadline does not fit in `Instant` (`Duration::MAX` does this). The panic runs after `reserve` and before `insert`, so those units stay reserved and `sweep_expired` has nothing to put back.

`confirm` `remove`s the hold before `ship` or `release` finishes. If `ship` returns `Insufficient`, or panics on `on_hand -= qty`, the id is already gone. The units stay reserved, and a later `confirm` or `sweep_expired` has no entry for them. The expiry path drops the hold before `release` returns as well.

ISSUES:
L47: available() does unchecked on_hand - reserved, so reserved > on_hand panics in debug and wraps in release
L81: receive() overwrites an existing SKU, dropping prior on_hand, reserved, name, and price
L101: release() saturating_sub's and returns Ok when qty > reserved, under-releasing and clearing other holds
L112: ship() subtracts qty from on_hand after checking only reserved, so on_hand < qty overflows
L120: record_loss() subtracts lost from on_hand with no check, overflowing and allowing reserved > on_hand
L127: total_value() multiplies and sums u64 with no overflow check (debug panic, release wrap)
L144: moving_average() assert-panics when window is 0
L157: deltas() reads prices[i + 1] while i runs through 0..len, so every non-empty slice panics out of bounds
L157: deltas() subtracts i64 with unchecked arithmetic (debug panic, release wrap)
L185: lookup() get_unchecked on a scanner-supplied slot is undefined behavior when the index is out of range
L196: append_batch() dereferences a pointer into buf after extend_from_slice, which is undefined behavior and a use-after-free if the Vec reallocates
L204: encode() casts name.len() to u8, so names longer than 255 bytes are framed with a truncated length and decode misreads them
L218: decode() uses from_utf8_unchecked on network bytes; invalid UTF-8 is undefined behavior
L245: Service lock().unwrap() panics if the mutex is poisoned (same pattern on the other Service locks)
L246: place_hold() reserves stock before the hold is inserted, so a later panic leaves units reserved with no hold
L253: Instant::now() + ttl panics when the deadline does not fit in Instant
L260: confirm() removes the hold before ship or release finishes, so a failed ship drops the id and sticks the reservation
L262: confirm() locks holds then warehouse, while place_hold and sweep_expired lock warehouse then holds, so those threads deadlock