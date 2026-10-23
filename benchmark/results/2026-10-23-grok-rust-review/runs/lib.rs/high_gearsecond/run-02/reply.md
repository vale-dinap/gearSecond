The module is in the message, so I am reviewing that source for logic errors, panics, overflow, undefined behaviour, and concurrency bugs.This module has unsound public functions, stock updates that panic or wrap, a `deltas` loop that panics on every non-empty slice, and a lock-order deadlock in `Service`.

## Stock accounting

`receive` builds a brand-new `Item` and `insert`s it at L81. A second receipt of the same SKU discards the quantity already on hand, the reserved count, the name, and the price. The doc comment says the new units are added to the existing row.

`record_loss` does `on_hand -= lost` at L120 with no comparison against `on_hand` or `reserved`. In debug that panics when `lost > on_hand`. In release it wraps, so a loss of 6 from 5 on hand becomes `u32::MAX - 0` (4294967294) and the stock value explodes. A smaller loss still breaks the shelf: 10 on hand, 8 reserved, lose 5, leaves `on_hand = 5` and `reserved = 8`.

`available` computes `on_hand - reserved` at L47. After that state, debug builds panic and release builds wrap to a huge "available" count. `reserve` then trusts that count and can wrap `reserved` as well. `low_stock` calls `available` and panics the same way.

`ship` only checks `qty` against `reserved`. `on_hand -= qty` at L112 is unchecked. With 5 on hand and 8 reserved, `ship(4)` succeeds and leaves `on_hand = 1`, `reserved = 4`. `ship(4)` again passes the reserved check, subtracts from `reserved`, then panics or wraps on `on_hand`. The reserved update is already stored if that subtraction panics.

`release` uses `saturating_sub` and returns `Ok` at L101 when `qty` is larger than `reserved`. The reserved count falls to zero while the caller is told the full release worked. Those units can be reserved again while a hold still records the old quantity.

`total_value` multiplies `on_hand as u64 * price_cents` and sums the products at L127. Either the multiply or the sum overflows `u64` for large prices. Debug builds panic. Release builds wrap and report a much smaller warehouse value. Overflow here is defined wraparound in release builds. The unsafe bugs below are undefined behaviour.

## Deltas

`deltas` sizes the output for `len - 1` elements, then loops `0..prices.len()` at L156 and reads `prices[i + 1]` at L157. The last iteration indexes one past the end, so every non-empty slice panics. An empty slice returns an empty vec. A one-element series panics before it can return the empty delta list.

On earlier pairs the subtraction can overflow `i64` (`i64::MIN - 1`, or `i64::MIN - i64::MAX`). Debug builds panic on that overflow. Release builds wrap.

`moving_average` rejects a zero window with `assert!`, which panics in release builds too. That one is an explicit guard.

## Unsound safe functions

`SlotTable::lookup` is a safe function and calls `get_unchecked` at L185. The argument is a scanner slot. An index past `slots.len()` is undefined behaviour. `assign` returns `Malformed` for the same bad index, so the two entry points disagree, and an empty table makes every lookup unsound.

`append_batch` takes a raw pointer to the element just pushed (L194), then calls `extend_from_slice` (L195), then dereferences that pointer (L196). `extend_from_slice` reallocates when the vec is full, which frees the buffer the pointer still addresses. A full buffer plus a non-empty tail is enough. The value it tries to read is the `head` it already copied into a local.

`encode` stores `name.len() as u8` at L204. A name longer than 255 bytes is truncated in the length prefix, while the full byte string is still appended. `decode` then treats later name bytes as the SKU and quantity and accepts the frame.

`decode` is documented as handling a network buffer and calls `from_utf8_unchecked` at L218. Any invalid UTF-8 sequence of the stated length is undefined behaviour. The length check around it is fine, and the `try_into().unwrap()` calls see exactly four bytes once that check has passed.

## Holds and locking

`place_hold` and `sweep_expired` lock `warehouse` and then `holds` (L245 then L247, L272 then L273). `confirm` locks `holds` and then `warehouse` (L259, then L262 or L265) and keeps the holds lock for the whole call. Two threads deadlock:

- Thread A is in `confirm`, holds `holds`, and waits for `warehouse`.
- Thread B is in `place_hold` or `sweep_expired`, holds `warehouse`, and waits for `holds`.

`place_hold` reserves stock, then evaluates `Instant::now() + ttl` at L253. A large `ttl` panics (`Duration::MAX` is enough), the hold is never inserted, and the units stay reserved. The panic poisons the `warehouse` and `holds` mutexes, so later `lock().unwrap()` calls panic too.

`confirm` `remove`s the hold at L260 before `release` or `ship` finishes. If `ship` returns `Insufficient`, or panics on the `on_hand` subtraction, that id is gone. Nothing in `sweep_expired` will put those units back, and a retry gets `NoSuchHold`.

`parse_command` and `SlotTable::assign` match their checks. The three tests stay on the short ASCII name and the single in-bounds ship, so they miss these paths.

ISSUES:
L47: available() subtracts reserved from on_hand and panics in debug or wraps in release when reserved is greater
L81: receive() inserts a new Item over an existing SKU, dropping prior on-hand quantity, reserved count, name, and price
L101: release() saturates reserved and returns Ok when qty exceeds reserved, so over-release is reported as success
L112: ship() subtracts qty from on_hand with no on_hand check, panicking or wrapping when on_hand is below qty
L120: record_loss() does an unchecked on_hand -= lost, which panics or wraps and can leave reserved above on_hand
L127: total_value() multiplies and sums u64 stock values with no overflow handling (debug panic, release wrap)
L156: deltas() loops through the last index and reads prices[i + 1], so every non-empty slice panics
L157: deltas() subtracts i64 prices directly, so a difference outside i64 panics in debug and wraps in release
L185: lookup() uses get_unchecked on a scanner slot, and an out-of-range index is undefined behaviour
L196: append_batch() dereferences a pointer into the Vec after extend_from_slice can reallocate, which is undefined behaviour
L204: encode() casts name.len() to u8, so a name longer than 255 bytes writes a corrupt length prefix
L218: decode() uses from_utf8_unchecked on network bytes, so invalid UTF-8 is undefined behaviour
L253: place_hold() panics when Instant::now() + ttl overflows, after reserve and before the hold is stored
L259: confirm() locks holds then warehouse while place_hold and sweep_expired lock warehouse then holds, so the calls deadlock
L260: confirm() removes the hold before release or ship finishes, so a failure leaks the reservation and the id cannot be retried