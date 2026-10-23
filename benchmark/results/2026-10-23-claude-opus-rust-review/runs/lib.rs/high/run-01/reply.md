# Review of `src/lib.rs`

Several of these defects should block the merge. Three are undefined behaviour in `unsafe` code, one is a deadlock, and several cause panics or silent stock corruption.

## Undefined behaviour / memory safety

**`SlotTable::lookup` (L185): out-of-bounds read on untrusted input.**
The doc comment says `slot` comes straight from a scanner message. `get_unchecked` with an out-of-range index is UB: it reads arbitrary memory, which is an information leak at best. The bounds check is one compare and costs almost nothing here. Use `self.slots.get(slot).copied().flatten()`.

**`append_batch` (L194–196): read through a dangling pointer.**
`first` points into `buf`'s heap allocation. `extend_from_slice(tail)` can reallocate the buffer, which frees the old allocation, so `*first` becomes a use-after-free. Read `head` directly (it's already a copy), or index `buf[start]` after extending.

**`decode` (L218): `from_utf8_unchecked` on network bytes.**
Building a `String` from invalid UTF-8 breaks a language invariant and is immediate UB. Later string operations can misbehave or read out of bounds. Use `std::str::from_utf8(...).map_err(|_| InvError::Malformed("bad utf-8"))?`.

## Concurrency

**`Service::confirm` (L259 vs L245/L272): lock-order inversion, so it can deadlock.**
`place_hold` and `sweep_expired` lock `warehouse` then `holds`. `confirm` locks `holds` first and then takes `warehouse` (L262/L265) while still holding it. If `confirm` runs concurrently with `place_hold` or `sweep_expired`, each thread can hold one lock and wait forever on the other. `confirm` should lock `warehouse` first, matching the other methods.

**Mutex poisoning amplifies every panic below.**
All locks use `.lock().unwrap()`. Any panic while a guard is held poisons the mutex, and every later call then panics. Examples are the `available()` underflow inside `reserve` and the `Instant + ttl` overflow. One bad request therefore takes down the whole service.

**`place_hold` (L253): `Instant::now() + ttl` panics on overflow.**
A huge `ttl` (e.g. `Duration::MAX`) panics. This happens after `reserve` has already succeeded, so the units stay reserved with no hold to ever release them, and both mutexes are poisoned. Use `checked_add` and validate it before reserving.

## Logic errors / integer overflow

**`Warehouse::receive` (L80–81): overwrites instead of adding.**
The doc says that for an existing SKU the units are added. The code replaces the whole `Item`, which discards existing `on_hand` and resets `reserved` to 0. Outstanding holds then refer to reservations that no longer exist. When such a hold is confirmed, `ship` fails with `Insufficient`, and because `confirm` has already removed the hold (L260), it is lost. Use `entry(sku)` and add `qty` with a checked add for existing items.

**`record_loss` (L120): unchecked subtraction.**
`on_hand -= lost` panics in debug builds and wraps in release builds when `lost > on_hand`. Even when it doesn't underflow, it can push `on_hand` below `reserved`, which breaks the invariant that `available()` and `ship()` depend on. Reject losses larger than `on_hand`. You also need to decide what happens to reserved units, e.g. clamp `reserved`, or reject losses that cut into reserved stock.

**`Item::available` (L47): underflow when `reserved > on_hand`.**
`record_loss` can produce that state (see above). In release builds the result wraps to roughly 4 billion, so `reserve` happily over-reserves. In debug builds it panics, and inside `Service` that panic poisons the mutex. The same broken state also lets `ship` underflow `on_hand` at L112.

**`total_value` (L127): u64 overflow.**
`on_hand as u64 * price_cents` and the `sum()` can both overflow, since `price_cents` is an unbounded `u64`. That is a panic in debug builds and a silently wrong total in release builds. Use `checked_mul`/`checked_add` and return `Option`, or accumulate in `u128`.

**`deltas` (L156–157): always indexes out of bounds.**
The loop runs `i` up to `len - 1` and reads `prices[i + 1]`, so it panics on every non-empty input. It should be `for i in 1..prices.len()` using `prices[i] - prices[i - 1]`, or `prices.windows(2)`. The `i64` subtraction can also overflow for extreme values; use `checked_sub` or `wrapping_sub` if that range matters.

**`encode` (L204): silent truncation of the name length.**
`name.len() as u8` truncates names of 256 bytes or more. The length prefix then disagrees with the bytes written, so `decode` reads the wrong bytes as the SKU and quantity, and can split the name in the middle of a UTF-8 character. Reject or truncate long names explicitly, at a char boundary, or widen the length field.

## Fine as written

The window handling in `moving_average`, `parse_command`, and the bounds arithmetic in `decode` (L215 cannot overflow because `len ≤ 255`) are correct. The existing tests don't exercise any of the paths above. Adding cases for `deltas`, `append_batch` with a large batch, invalid UTF-8 in `decode`, `receive` on an existing SKU, and `record_loss` beyond stock would catch most of these.

ISSUES:
L185: `get_unchecked` with untrusted scanner slot index, out-of-bounds read (UB)
L196: dereferences pointer into `buf` after `extend_from_slice` may have reallocated, use-after-free (UB)
L218: `from_utf8_unchecked` on untrusted network bytes, invalid `String` (UB)
L259: `confirm` locks `holds` then `warehouse`, opposite order to `place_hold`/`sweep_expired`, deadlock
L253: `Instant::now() + ttl` panics on overflow after stock is reserved; leaks reservation and poisons mutexes
L81: `receive` replaces existing item instead of adding qty; loses stock and resets `reserved`, orphaning holds
L120: `record_loss` unchecked `on_hand -= lost` underflows and can drop `on_hand` below `reserved`
L47: `on_hand - reserved` underflows when `reserved > on_hand` (panic in debug, huge availability in release)
L127: `on_hand * price_cents` and the sum can overflow u64
L157: `prices[i + 1]` indexes out of bounds on the last iteration; panics for any non-empty input
L204: `name.len() as u8` truncates names of 256+ bytes, producing corrupt records