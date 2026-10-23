# Review of `src/lib.rs`

The module has two sources of **undefined behaviour from untrusted input**, a **use-after-free**, a **lock-order deadlock**, and several logic and overflow bugs. It should not be merged as is.

## Memory safety / undefined behaviour

**`SlotTable::lookup` (L185): out-of-bounds read.**
- `get_unchecked(slot)` is called with a `slot` that, per the doc comment, "comes straight from a handheld scanner message."
- Any `slot >= slots.len()` is UB: it reads out of bounds and may return garbage or crash.
- The saved bounds check is a single compare. Use `self.slots.get(slot).copied().flatten()`.

**`append_batch` (L194–196): use-after-free.**
- `first` is a raw pointer into `buf`'s heap allocation.
- `extend_from_slice(tail)` may reallocate, which frees that allocation.
- `*first` then reads freed memory.
- No `unsafe` is needed here. Just return `head`, or read `buf[start]` after extending.

**`decode` (L218): unchecked UTF-8 on network data.**
- `from_utf8_unchecked` on bytes received from the network is UB if they aren't valid UTF-8.
- Every later `&str` operation on that `String` then relies on a broken invariant.
- Use `std::str::from_utf8(..).map_err(|_| InvError::Malformed("bad utf-8"))?`.

## Concurrency

**`Service::confirm` (L259 vs L245/247 and L272/273): deadlock from inconsistent lock order.**
- `place_hold` and `sweep_expired` lock `warehouse` and then `holds`.
- `confirm` locks `holds` and then `warehouse` (L262 / L265), while still holding `holds`.
- Two threads running `confirm` and `place_hold` (or `sweep_expired`) at the same time can each grab their first lock and wait forever for the other.
- Fix: take `warehouse` first in `confirm` as well, or use a single `Mutex` around both maps (plus the id counter).

## Logic errors

**`receive` (L80–81): overwrites existing stock.**
- The doc says units are *added* to an existing SKU.
- Instead, `insert` replaces the whole `Item`. It discards the existing `on_hand` and also resets `reserved` to 0 while holds are outstanding.
- When those holds are later confirmed, `ship` fails with `Insufficient`. Expiry/release is silently absorbed by `saturating_sub`.
- Use `entry(sku)` and `on_hand += qty`, ideally with `checked_add`.

**`deltas` (L156–157): always panics on non-empty input.**
- The loop runs `i` up to `len - 1`, so `prices[i + 1]` indexes out of bounds on the last iteration.
- It should iterate `0..len-1`, or use `prices.windows(2).map(|w| w[1] - w[0])`.
- The `i64` subtraction can also overflow for extreme values.

## Integer underflow / overflow

These panic in debug builds and silently wrap in release builds, which corrupts stock counts.

**`record_loss` (L120): unchecked subtraction.**
- `on_hand -= lost` underflows if `lost > on_hand`.
- Even without underflow, it can push `on_hand` below `reserved`, which breaks the invariant `reserved <= on_hand` that other code relies on.

**`Item::available` (L47): underflow once the invariant is broken.**
- `on_hand - reserved` underflows after the `record_loss` case above.
- This makes `reserve` and `low_stock` panic, or in release builds report about 4 billion units available.

**`ship` (L112): underflow once the invariant is broken.**
- `on_hand -= qty` only checks `qty <= reserved`.
- If a loss has pushed `on_hand < reserved`, this underflows.

**`total_value` (L127): overflow.**
- `on_hand as u64 * price_cents` and the `sum()` can overflow `u64` for large prices.
- Use `checked_mul`/`checked_add`, or widen to `u128`.

**`encode` (L204): silent length truncation.**
- `name.len() as u8` truncates names longer than 255 bytes.
- The length prefix then disagrees with the payload, so `decode` reads part of the name as SKU/qty, or the record is rejected.
- Reject or truncate long names explicitly (on a char boundary).

**`place_hold` (L253): `Instant` overflow.**
- `Instant::now() + ttl` panics on overflow with a very large `ttl` (e.g. `Duration::MAX`).
- Use `checked_add` and return an error instead.

## Minor note
`release` (L101) uses `saturating_sub`, so releasing more than is reserved returns `Ok`. This masks accounting errors, such as a stray `RELEASE` command consuming units that belong to a hold. Consider returning `Insufficient` instead.

ISSUES:
L185: `get_unchecked` with untrusted scanner-supplied slot index; out-of-bounds read is UB
L196: raw pointer into `buf` dereferenced after `extend_from_slice` may reallocate; use-after-free
L218: `from_utf8_unchecked` on network bytes; invalid UTF-8 is UB
L259: `confirm` locks `holds` then `warehouse`, the reverse of `place_hold`/`sweep_expired`; lock-order deadlock
L81: `receive` replaces an existing item instead of adding to it, losing on-hand stock and outstanding reservations
L157: `prices[i + 1]` indexes out of bounds on the last iteration; `deltas` always panics on non-empty input
L120: `on_hand -= lost` unchecked; underflows and can drop `on_hand` below `reserved`
L47: `on_hand - reserved` underflows once `reserved > on_hand`
L112: `on_hand -= qty` can underflow when `on_hand < reserved`
L127: `on_hand * price_cents` and the sum can overflow `u64`
L204: `name.len() as u8` truncates names over 255 bytes, producing corrupt records
L253: `Instant::now() + ttl` panics on overflow for large `ttl`