# Review of `src/lib.rs`

This module has several merge-blocking defects: three sources of undefined behaviour in safe-looking public APIs, a lock-order deadlock, and stock-accounting bugs that can underflow and panic.

## Undefined behaviour / memory safety

**`SlotTable::lookup` (L185)**: `get_unchecked(slot)` is called on a `slot` that the doc comment says "comes straight from a handheld scanner message". Any out-of-range value is an out-of-bounds read, which is UB, through a *safe* public function. Use `self.slots.get(slot).copied().flatten()`. The bounds check costs almost nothing here.

**`append_batch` (L194–196)**: `first` is a raw pointer into `buf`'s allocation, taken before `extend_from_slice(tail)`. That call can reallocate, so `*first` may read freed memory (use-after-free). `wrapping_add` only avoids UB in the pointer arithmetic, not in the dereference. The fix needs no unsafe code: the value is simply `head`, so return `Some((head, buf.len()))`.

**`decode` (L218)**: `from_utf8_unchecked` runs on bytes "received from the network". Building a `str` from invalid UTF-8 is UB, and later string operations may misbehave. Use `std::str::from_utf8(&rest[..len]).map_err(|_| InvError::Malformed("bad utf-8"))?`.

## Concurrency

**Lock-order inversion between `confirm` and `place_hold`/`sweep_expired` (L259 vs L245–247 / L272–273)**:
- `place_hold` and `sweep_expired` lock `warehouse` and then `holds`.
- `confirm` locks `holds` and then, while still holding it, locks `warehouse` (L262 / L265).

If two threads run these concurrently, each can hold one mutex and wait forever for the other, which is a classic ABBA deadlock. Fix it with one global order: in `confirm`, lock `warehouse` first, or remove the hold and drop the `holds` guard before touching the warehouse.

## Logic errors / panics / overflow

**`receive` (L80–81)**: The doc says units are *added* to an existing SKU, but the code `insert`s a fresh `Item`. This causes two problems:
- Existing `on_hand` is discarded.
- `reserved` is reset to 0 while holds are still outstanding. A later `confirm` → `ship` then fails with `Insufficient` (the hold has already been removed, so it is lost), and `release` silently does nothing because of the `saturating_sub`.

Use `entry(sku)` and add to `on_hand` with a checked add when the SKU exists.

**`record_loss` (L120)**: `on_hand -= lost` has no validation.
- If `lost > on_hand`, it panics in debug builds and wraps to roughly 4 billion units in release.
- Even when it doesn't underflow, it can leave `on_hand < reserved`, which breaks the invariant the rest of the code relies on. In that state:
  - `available()` (L47) underflows on `on_hand - reserved`, so `reserve` and `low_stock` panic or wrap.
  - `ship` (L112), which only checks `qty <= reserved`, can underflow `on_hand`.

Reject `lost > on_hand`, and decide what happens to reservations that exceed the remaining stock. At minimum, `available()` should use `saturating_sub`.

**`total_value` (L127)**: `on_hand as u64 * price_cents` and the `.sum()` are unchecked. A price above about $42.9M combined with a full `u32` quantity, or the sum across many SKUs, overflows `u64`. That panics in debug and silently gives a wrong total in release. Use `checked_mul`/`checked_add` or accumulate in `u128`.

**`deltas` (L156–157)**: The loop runs `i` up to `len - 1`, so `prices[i + 1]` is always out of bounds on the last iteration. The function panics for every non-empty input. Use `prices.windows(2).map(|w| w[1] - w[0])`. The subtraction can also overflow for extreme `i64` values; consider `checked_sub` or `i128`.

**`encode` (L204)**: `name.len() as u8` silently truncates names of 256 bytes or more. The full name is still written, so the length prefix disagrees with the payload. `decode` then reads the wrong bytes as the name, SKU and quantity, or rejects the record. Return an error, or cap the name at 255 bytes on a UTF-8 boundary.

**`place_hold` (L253)**: `Instant::now() + ttl` panics on overflow if a caller passes a huge `ttl` (e.g. `Duration::MAX`). It also panics *after* `reserve` succeeded, while the mutexes are held. That poisons both locks, so every later `.unwrap()` on them panics. Use `checked_add` and validate before reserving.

## Minor note

`confirm`, L260–266: if `ship` fails, the hold has already been removed but its reservation stays, so stock leaks. Today this is only reachable through the `receive`/`record_loss` bugs above, but it is worth making robust.

ISSUES:
L185: `get_unchecked` with untrusted scanner index, out-of-bounds read (UB) via safe API
L196: dereferences pointer taken before `extend_from_slice` may reallocate (use-after-free, UB)
L218: `from_utf8_unchecked` on network bytes, invalid UTF-8 `str` (UB)
L259: `confirm` locks holds then warehouse, opposite order to `place_hold`/`sweep_expired`, deadlock
L81: `receive` overwrites existing item instead of adding stock; resets `reserved`, orphaning outstanding holds
L120: `record_loss` unchecked subtraction underflows and can push `on_hand` below `reserved`
L47: `available()` underflows when `on_hand < reserved`
L112: `ship` can underflow `on_hand` when `on_hand < reserved`
L127: `total_value` multiplication/sum can overflow `u64`
L157: `deltas` indexes `prices[i + 1]` out of bounds on last iteration, panics for any non-empty input
L204: `name.len() as u8` truncates names ≥256 bytes, producing corrupt records
L253: `Instant::now() + ttl` can panic on overflow after reserving and while locks are held (poisons mutexes)