# Review of `src/lib.rs`

## Memory safety / undefined behaviour

**`SlotTable::lookup` (L185).** `get_unchecked(slot)` is called with an index that, per the doc comment, comes straight from a handheld scanner message. Any out-of-range slot is an out-of-bounds read, which is undefined behaviour. This is not a panic; it can return garbage or crash later. Use `self.slots.get(slot).copied().flatten()`. The bounds check costs essentially nothing next to network I/O.

**`append_batch` (L194–L196).** `first` is a raw pointer into `buf`'s allocation. `extend_from_slice(tail)` may reallocate, which frees the old buffer. Dereferencing `first` afterwards is a use-after-free. The value is already known: return `head` directly, or re-index with `buf[start]` after extending.

**`decode` (L218).** `from_utf8_unchecked` runs on bytes received from the network. Invalid UTF-8 inside a `String` is undefined behaviour, and later string operations may read out of bounds. Use `std::str::from_utf8(...).map_err(|_| InvError::Malformed("name not utf-8"))?`.

## Concurrency

**Lock-order inversion between `confirm` and `place_hold` / `sweep_expired` (L259 vs L245/L247, L272/L273).**
- `place_hold` and `sweep_expired` lock `warehouse` first, then `holds`.
- `confirm` locks `holds` first (L259), then `warehouse` (L262 or L265), while still holding `holds`.

Two threads running `confirm` and `place_hold` concurrently can each hold one lock and wait forever for the other. That is a deadlock. Pick one order everywhere: take `warehouse` before `holds` in `confirm`, or drop `holds` before locking `warehouse`.

## Logic errors

**`receive` (L80–L81).** The doc says units for an existing SKU are added to what is already on hand. The code instead replaces the whole `Item`:
- Existing stock is lost.
- `reserved` is reset to 0 even though live holds still reference those units.

When those holds are later confirmed, `ship` fails with `Insufficient`. When they are released, `saturating_sub` silently hides the inconsistency. Use the `entry` API and do `on_hand += qty`, which should itself be checked for overflow.

**`record_loss` (L120).** Losses are not validated. `on_hand -= lost` underflows when `lost > on_hand`: it panics in debug and wraps to roughly 4 billion units in release. Even without underflow, it can push `on_hand` below `reserved`, which breaks the invariant `reserved <= on_hand` that the rest of the code relies on. Return `Insufficient` when `lost > on_hand`. Also decide what happens to reservations that are no longer backed by stock.

**`Item::available` (L47)** and **`ship` (L112).** Both subtract assuming `reserved <= on_hand`. Once `record_loss` breaks that invariant:
- `available()` underflows. It panics in debug; in release it reports a huge availability, so `reserve` over-commits.
- `ship` underflows `on_hand`.

The fix belongs mainly in `record_loss`. `available` could also use `saturating_sub` defensively.

**`deltas` (L156–L157).** The loop runs `i` up to `len - 1` and reads `prices[i + 1]`, so it always panics with index out of bounds on any non-empty input. The loop should be `for i in 1..prices.len()` using `prices[i] - prices[i - 1]`, or `prices.windows(2)`. The `i64` subtraction can also overflow for extreme values; use `checked_sub` or `wrapping_sub` if inputs are not trusted.

**`encode` (L204).** `name.len() as u8` silently truncates names of 256 bytes or more. The length prefix then disagrees with the bytes written, so `decode` reads part of the name as the SKU and quantity. Reject or truncate long names explicitly, on a UTF-8 char boundary. Truncating there also prevents producing invalid UTF-8.

**`total_value` (L127).** `on_hand as u64 * price_cents` and the `sum()` can overflow `u64` with large prices, which `price_cents: u64` allows. That panics in debug and wraps in release. Use `checked_mul` / `checked_add`, or `u128`.

## Notes (not defects)
- `moving_average` is correct, including the case `window > len`, which yields an empty vector.
- `parse_command` and the bounds checks in `decode` are fine. `len + 8` cannot overflow because `len <= 255`.
- The existing tests do not cover any of the paths above. A test for `deltas` on a non-empty slice would have caught that bug immediately.

ISSUES:
L185: get_unchecked with untrusted scanner slot index is out-of-bounds UB
L196: raw pointer dereferenced after extend_from_slice may have reallocated (use-after-free)
L218: from_utf8_unchecked on network bytes is UB for invalid UTF-8
L259: confirm locks holds then warehouse, opposite order to place_hold/sweep_expired, so it can deadlock
L81: receive replaces existing item, losing on-hand stock and resetting reserved despite live holds
L120: record_loss subtracts without checks, underflowing on_hand and allowing on_hand < reserved
L47: available() underflows when reserved > on_hand
L112: ship can underflow on_hand once reserved > on_hand
L157: deltas indexes prices[i + 1] past the end, so it panics on every non-empty input
L204: name length cast to u8 truncates names of 256+ bytes and corrupts the record
L127: total_value multiplication/sum can overflow u64