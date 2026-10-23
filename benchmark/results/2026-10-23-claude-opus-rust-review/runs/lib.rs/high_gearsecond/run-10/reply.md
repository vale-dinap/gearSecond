Ten defects below. Four are undefined behaviour that can be triggered from safe callers or untrusted input, and one is a lock-order deadlock in `Service`.

## Undefined behaviour / memory safety

**L185, `SlotTable::lookup`.** `get_unchecked(slot)` is called with a `slot` that the doc comment says "comes straight from a handheld scanner message". Any out-of-range value is an out-of-bounds read, which is UB, from a safe `pub fn`. Use `self.slots.get(slot).copied().flatten()`. The bounds check is negligible next to the network I/O that delivered the slot.

**L194–196, `append_batch`.** `first` is a raw pointer into `buf`'s heap allocation. `extend_from_slice(tail)` can then reallocate, so `*first` reads freed memory (use-after-free). `wrapping_add` does nothing to prevent this. The value is already known, so just return `head`. Otherwise, read `buf[start]` after the extend.

**L218, `decode`.** `from_utf8_unchecked` is applied to bytes received from the network. A `String` holding invalid UTF-8 breaks a language invariant and is UB. Use `std::str::from_utf8(..).map_err(|_| InvError::Malformed("bad utf-8"))?`.

## Concurrency

**L259/262/265 vs L245/247 and L272/273, lock-order inversion.** `place_hold` and `sweep_expired` lock `warehouse` then `holds`. `confirm` locks `holds` then `warehouse`, while still holding `holds`. If `confirm` runs concurrently with either of the others, the two threads can deadlock. Pick one order (warehouse → holds) and use it everywhere. Alternatively, drop the `holds` guard after `remove` and before touching the warehouse.

## Logic errors

**L80–81, `receive`.** The doc says units for an existing SKU are *added*. Instead, `insert` replaces the whole `Item`:
- `on_hand` is lost.
- `reserved` is reset to 0 while holds are still outstanding.
- Later, `confirm` → `ship` fails with `Insufficient`. The hold has already been removed by then, so the shipment is lost.

Use the `entry` API, and add with `checked_add` (or saturating, by policy).

**L156–157, `deltas`.** The loop runs `i` up to `len-1`, so `prices[i + 1]` indexes out of bounds on the last iteration. This panics for every non-empty input. Iterate `0..prices.len().saturating_sub(1)` or use `prices.windows(2)`. The subtraction can also overflow for extreme `i64` values. Use `checked_sub` if the inputs are untrusted.

**L204, `encode`.** `name.len() as u8` silently truncates names of 256 bytes or more. The length prefix then disagrees with the payload, and `decode` reads part of the name as the SKU and qty. Reject or truncate long names explicitly, ideally at a UTF-8 char boundary.

## Integer overflow / panics

**L120, `record_loss`.** `on_hand -= lost` underflows if `lost > on_hand`: a panic in debug builds, a wrap to roughly 4 billion in release. It can also leave `on_hand < reserved` without underflowing, which breaks the invariant everything else relies on:
- **L47:** `available()` then underflows. It is called from `reserve` and `low_stock`.
- **L112:** `ship`'s `on_hand -= qty` can underflow.

Validate `lost <= on_hand`, and decide policy for losses that eat into reserved stock. For example, also reduce `reserved` and flag the affected holds.

**L127, `total_value`.** `on_hand as u64 * price_cents` and the `sum()` can overflow `u64` when prices are large. This panics in debug and gives wrong totals in release. Use `checked_mul` and `checked_add` (returning `Option`/`Result`), or accumulate in `u128`.

**L253, `place_hold`.** `Instant::now() + ttl` panics if a caller passes a huge `ttl`. When that happens, the stock was already reserved at L246, so the reservation leaks. Use `checked_add`, and reserve only after it succeeds.

### Minor note

`release` (L101) uses `saturating_sub`, and the text protocol exposes `RELEASE`. Together they let any client release units that belong to someone else's hold. That hold's later `confirm` then fails. Consider whether `RELEASE` should be limited to hold IDs.

ISSUES:
L185: `get_unchecked` with untrusted scanner index, out-of-bounds read (UB)
L196: dereferences pointer into `buf` after `extend_from_slice` may have reallocated (use-after-free)
L218: `from_utf8_unchecked` on network input, invalid-UTF-8 `String` (UB)
L259: `confirm` locks holds then warehouse, opposite order to `place_hold`/`sweep_expired`, deadlock
L81: `receive` overwrites existing item instead of adding, losing `on_hand` and resetting `reserved` under live holds
L157: `deltas` indexes `prices[i + 1]` past end, panics on any non-empty input
L204: `name.len() as u8` truncates names of 256+ bytes, corrupt wire record
L120: `record_loss` can underflow `on_hand` or push it below `reserved`
L47: `available()` underflows when `on_hand < reserved`
L112: `ship` `on_hand -= qty` can underflow once invariant broken
L127: `total_value` multiplication/sum can overflow u64
L253: `Instant::now() + ttl` can panic after stock already reserved, leaking the reservation