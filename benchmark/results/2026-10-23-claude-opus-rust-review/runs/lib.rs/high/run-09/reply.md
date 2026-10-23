# Review of `src/lib.rs`

The module has several merge-blocking defects: three sources of undefined behaviour in `unsafe` blocks, a lock-order deadlock in `Service`, a guaranteed panic in `deltas`, and stock-accounting bugs that let `on_hand` drop below `reserved`.

## Undefined behaviour

- **`SlotTable::lookup` (L185).** `get_unchecked(slot)` is used on a `slot` that the doc comment says "comes straight from a handheld scanner message." Any out-of-range value is an out-of-bounds read, which is UB. One bad scan can return garbage or crash the process. Use `self.slots.get(slot).copied().flatten()`. The bounds check costs effectively nothing next to the network I/O.
- **`append_batch` (L194–196).** `first` is a raw pointer into the buffer, taken before `extend_from_slice(tail)`. If that call reallocates, `first` dangles and `*first` is a use-after-free. Read `buf[start]` after the extend, or just return `head`, which is already the value.
- **`decode` (L218).** `from_utf8_unchecked` is applied to bytes from the network. A `String` holding invalid UTF-8 breaks a language invariant, so this is UB. Use `std::str::from_utf8(..).map_err(|_| InvError::Malformed("bad utf-8"))?`.

## Concurrency

- **Deadlock between `confirm` and `place_hold`/`sweep_expired` (L259 vs L245/L247 and L272/L273).**
  - `place_hold` and `sweep_expired` lock `warehouse` first, then `holds`.
  - `confirm` locks `holds` first and, while still holding it, locks `warehouse` (L262 or L265).
  - If two threads run these concurrently, each can hold one lock while waiting for the other (an ABBA deadlock).
  - Fix: always take `warehouse` before `holds`. Alternatively, in `confirm`, remove the hold, drop the `holds` guard, and only then lock `warehouse`.

## Panics and integer overflow

- **`deltas` (L156–157).** The loop runs `i` up to `prices.len() - 1`, so `prices[i + 1]` is out of bounds on the last iteration. It panics for every non-empty input. Iterate `0..prices.len().saturating_sub(1)` or use `prices.windows(2)`. The `i64` subtraction can also overflow on extreme values; `checked_sub`/`wrapping_sub` would make that explicit.
- **`Item::available` (L47).** `on_hand - reserved` underflows whenever `reserved > on_hand`. Bugs elsewhere make that state reachable (see `record_loss` and `receive` below).
  - Debug builds panic.
  - Release builds wrap to roughly 4 billion "available" units, so `reserve` will accept an oversell.
- **`record_loss` (L120).** `on_hand -= lost` has no check.
  - If `lost > on_hand`, it underflows: a panic in debug, a near-`u32::MAX` count in release.
  - If `lost` exceeds unreserved stock, `on_hand` drops below `reserved`. That breaks `available()` and can later make `ship` underflow at L112.
  - It should return `InvError::Insufficient`, or at least check `lost <= on_hand` and decide on a policy for reserved units.
- **`total_value` (L127).** `on_hand as u64 * price_cents` and the `.sum()` are unchecked. Large prices times quantities overflow `u64`: a panic in debug, a silently wrong total in release. Use `checked_mul`/`checked_add` or a `u128` accumulator.
- **`place_hold` (L253).** `Instant::now() + ttl` panics if a caller passes a huge `ttl`, such as `Duration::MAX`. Use `checked_add` and return an error.

## Logic errors

- **`receive` (L80–81).** The doc says units are added to an existing SKU's stock. In fact the code always inserts a fresh `Item`, so it:
  - replaces `on_hand` with `qty` instead of adding to it,
  - resets `reserved` to 0.

  The second effect wipes every outstanding reservation. Any active hold on that SKU then fails in `confirm` at L266 with `Insufficient`. Because the hold was already removed at L260, the error is unrecoverable. Use `entry(sku)`: add `qty` to `on_hand` (with `checked_add`) for existing items, and insert only when the SKU is absent.
- **`encode` (L204).** `name.len() as u8` silently truncates names of 256 bytes or more. The length prefix then disagrees with the payload, so `decode` reads part of the name as the SKU and quantity. This produces a well-formed but wrong record, not an error. Reject or truncate long names explicitly, ideally on a UTF-8 character boundary.

## Tests

The tests miss every issue above:
- No test exercises `deltas`, `receive` on an existing SKU, `record_loss`, non-UTF-8 or oversized names, or concurrent `Service` use.
- Running the suite under Miri would flag the `append_batch` and `get_unchecked` UB.

ISSUES:
L185: `get_unchecked` with untrusted scanner-supplied slot index; out-of-bounds read is UB
L196: raw pointer taken before `extend_from_slice` may reallocate; dereference is use-after-free UB
L218: `from_utf8_unchecked` on network bytes; invalid UTF-8 in a `String` is UB
L259: `confirm` locks `holds` then `warehouse`, opposite order from `place_hold`/`sweep_expired`; deadlock
L157: `deltas` indexes `prices[i + 1]` on the last iteration; panics for any non-empty input
L47: `on_hand - reserved` underflows when `reserved > on_hand`; panic in debug, oversell in release
L120: `record_loss` subtracts without checks; underflows and can push `on_hand` below `reserved`
L127: `on_hand * price_cents` and the sum can overflow `u64`
L253: `Instant::now() + ttl` panics on a large caller-supplied ttl
L81: `receive` overwrites an existing item instead of adding stock, resetting `on_hand` and wiping `reserved`
L204: `name.len() as u8` truncates names of 256+ bytes, producing corrupt records