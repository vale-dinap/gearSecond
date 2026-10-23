Here are the defects I found, roughly in order of severity.

## Memory safety / undefined behaviour

**L185 – `SlotTable::lookup` uses `get_unchecked` on untrusted input.** The doc comment says `slot` comes straight from a scanner message, so any value ≥ `slots.len()` is an out-of-bounds read. That is UB in safe-looking public API. Use `self.slots.get(slot).copied().flatten()`. The bounds check costs almost nothing compared with the UB.

**L194–196 – `append_batch` reads through a dangling pointer.** `first` is taken from `buf.as_ptr()`. Then `extend_from_slice(tail)` may reallocate the vector, which frees the old allocation, and `*first` reads freed memory. That is use-after-free UB. The value is just `head` anyway, so return `head` and drop the pointer entirely.

**L218 – `decode` calls `from_utf8_unchecked` on network bytes.** A peer can send invalid UTF-8 and produce a `String` that violates its invariant, which is UB. Use `std::str::from_utf8(&rest[..len]).map_err(|_| InvError::Malformed("bad utf-8"))?`.

## Concurrency

**L259 / L262 / L265 vs L245–247 and L272–273 – lock-order inversion causes deadlock.**
- `place_hold` and `sweep_expired` lock `warehouse` and then `holds`.
- `confirm` locks `holds` and then `warehouse`, while still holding `holds`.

If `confirm` runs concurrently with either of the other two, each thread can hold one lock and wait forever for the other. Pick one global order (warehouse, then holds) and use it everywhere. Alternatively, drop the `holds` guard in `confirm` before touching the warehouse.

**L253 – `Instant::now() + ttl` panics on overflow.** `ttl` is supplied by the caller, so a huge value (e.g. `Duration::MAX`) panics. The panic also happens after `reserve` has already succeeded at L246, so those units stay reserved forever. Compute the expiry with `checked_add` before reserving, and return an error if it fails.

## Logic errors

**L80–81 – `receive` overwrites instead of adding.** The doc says units for an existing SKU are added to what is on hand. Instead, `insert` replaces the whole `Item`, which:
- discards the existing `on_hand`,
- resets `reserved` to 0 while holds still reference those units.

After that, `ship` and `release` from outstanding holds act on wrong counts. Use the `entry` API and add with `checked_add` or `saturating_add`.

**L156–157 – `deltas` always panics on non-empty input.** The loop runs `i` up to `len-1`, so `prices[i + 1]` is out of bounds on the last iteration. Iterate `prices.windows(2)` or use `1..prices.len()`. The subtraction can also overflow for extreme `i64` values; `checked_sub` or `wrapping_sub` would make that explicit.

**L204 – `encode` silently truncates name length.** `name.len() as u8` wraps for names over 255 bytes. The length byte then disagrees with the payload, so `decode` misparses the record, and the receiver gets wrong SKU and qty values instead of an error. Reject or truncate long names explicitly, ideally at a UTF-8 boundary, or widen the length field.

## Integer overflow / underflow

**L120 – `record_loss` subtracts without checking.** If `lost > on_hand`, this panics in debug builds and wraps to roughly 4 billion units in release builds. Even when it doesn't underflow, it can push `on_hand` below `reserved`, which breaks the invariant the rest of the code relies on. Validate `lost` and decide how to handle reservations that are no longer backed by stock.

**L47 – `available` underflows when `reserved > on_hand`.** Once L120 has broken the invariant, `on_hand - reserved` panics or wraps. That affects `reserve` (the wrap would allow over-reserving) and `low_stock`. Use `saturating_sub`, and fix the root cause in L120.

**L112 – `ship` can underflow `on_hand`.** This happens through the same broken invariant: `qty <= reserved` no longer implies `qty <= on_hand` after a loss.

**L127 – `total_value` can overflow.** `on_hand as u64 * price_cents` and the `sum()` are unchecked, and `price_cents` is an arbitrary `u64`. Large values panic in debug and wrap silently in release. Use `checked_mul` and `checked_add`, or accumulate in `u128`.

## Minor

**L101 – `release` hides accounting bugs.** `saturating_sub` silently accepts releasing more units than are reserved. Returning `Insufficient` would surface the bug instead of masking it.

ISSUES:
L185: get_unchecked with untrusted scanner slot index -> out-of-bounds read (UB)
L196: pointer into Vec read after extend_from_slice may reallocate -> use-after-free (UB)
L218: from_utf8_unchecked on network data -> invalid String (UB)
L259: confirm locks holds then warehouse, opposite order to place_hold/sweep_expired -> deadlock
L253: Instant::now() + caller ttl can panic on overflow, after stock already reserved (leaked reservation)
L81: receive overwrites existing item (loses on_hand, resets reserved) instead of adding units
L157: deltas indexes prices[i + 1] past end -> always panics on non-empty input
L204: name.len() as u8 truncates names > 255 bytes -> corrupt record, misparsed on decode
L120: record_loss unchecked subtraction underflows and can drop on_hand below reserved
L47: available() underflows when reserved > on_hand
L112: ship can underflow on_hand once reserved > on_hand
L127: total_value multiplication/sum can overflow u64
L101: release silently saturates over-release instead of reporting an error