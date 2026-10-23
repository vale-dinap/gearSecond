I found four memory-safety bugs (undefined behaviour), a deadlock, and several logic and overflow bugs. The most serious are listed first.

## Undefined behaviour

**`SlotTable::lookup` (L185): out-of-bounds read.**
- `slot` comes straight from a scanner message, but `get_unchecked` skips the bounds check.
- Any `slot >= slots.len()` reads past the allocation, so a bad scanner message causes UB.
- Fix: use `self.slots.get(slot).copied().flatten()`. The bounds check is negligible next to the lookup itself.

**`append_batch` (L194–196): dangling pointer.**
- `first` points into `buf`'s heap buffer.
- `extend_from_slice(tail)` can reallocate, which frees that buffer, and then `*first` reads freed memory.
- The `unsafe` is pointless anyway: `head` is already a copy of the value, so return `head` (or `buf[start]`).

**`decode` (L218): unvalidated UTF-8 from the network.**
- `from_utf8_unchecked` on untrusted bytes creates a `str` that is not valid UTF-8, which is immediate UB.
- Downstream string operations can then misbehave.
- Fix: use `std::str::from_utf8(...).map_err(|_| InvError::Malformed("bad utf-8"))?`.

## Concurrency

**`Service::confirm` (L259 and L262/L265): lock-order inversion, which can deadlock.**
- `place_hold` and `sweep_expired` take `warehouse`, then `holds`.
- `confirm` takes `holds`, then `warehouse`.
- If `confirm` runs at the same time as `place_hold` or `sweep_expired`, each thread can hold one lock while waiting for the other.
- Fix: take `warehouse` first in `confirm` as well, or drop the `holds` guard after `remove` and before locking `warehouse`.

**`place_hold` (L253): possible panic.**
- `Instant::now() + ttl` panics on overflow when given a very large `ttl` (e.g. `Duration::MAX`).
- It panics while both locks are held, so it also poisons them, and every later `unwrap()` panics.
- Fix: use `checked_add` and return an error on overflow.

## Logic errors and integer overflow

**`Warehouse::receive` (L80–81): overwrites instead of adding.**
- The doc says that for an existing SKU, units are added to what is on hand. The code replaces the whole `Item` instead.
- This throws away the existing `on_hand` and resets `reserved` to 0.
- Any outstanding holds then point at reservations that no longer exist: `confirm` → `ship` fails with `Insufficient`, and stock can be over-reserved.
- Fix: use `entry(sku)` and add `qty` to an existing item's `on_hand` with a checked add, keeping `reserved` unchanged.

**`record_loss` (L120): unchecked subtraction that can break the stock invariant.**
- If `lost > on_hand`, the subtraction underflows: it panics in debug builds and wraps to roughly 4 billion units in release builds.
- Even without underflow, it can push `on_hand` below `reserved`. That breaks the invariant `reserved <= on_hand` that other code relies on.
- Fix: validate `lost` against `on_hand`, and decide what happens to reservations that exceed what is left.

**`Item::available` (L47) and `ship` (L112): underflow once the invariant is broken.**
- After the `record_loss` problem above, `on_hand - reserved` underflows. That affects `available()`, `reserve` and `low_stock`.
- `ship` checks `qty` against `reserved` but not against `on_hand`, so `on_hand -= qty` can underflow too.
- In release builds these wrap silently: `available()` reports billions of units, and `reserve` then over-commits stock.

**`total_value` (L127): unchecked arithmetic.**
- `on_hand as u64 * price_cents`, and the `.sum()`, can overflow `u64` when prices are large.
- In release builds that gives a silently wrong total.
- Fix: use `checked_mul`/`checked_add`, or accumulate in `u128`.

**`deltas` (L156–157): always panics for non-empty input.**
- The loop runs `i` up to `len - 1`, so `prices[i + 1]` indexes out of bounds on the last iteration.
- The loop should be `for i in 1..prices.len()` with `prices[i] - prices[i - 1]`, or use `prices.windows(2)`.
- The subtraction can also overflow `i64`; `checked_sub` or `wrapping_sub` would handle that, depending on what is wanted.

**`encode` (L204): silent truncation of the name length.**
- `name.len() as u8` truncates names longer than 255 bytes.
- The record then has the wrong length prefix, so `decode` reads part of the name as the SKU and quantity.
- Fix: reject long names (return a `Result`), or use a wider length field.

**Holds versus receive and loss: missing cross-check (a consequence of the bugs above).**
- `confirm` (L266) removes the hold before `ship` is attempted. If `ship` fails, for example because `receive` reset `reserved`, the hold is lost with no rollback.

Nothing else stood out. `moving_average`, `parse_command`, and `reserve`'s `reserved += qty` (bounded by `available`) look correct.

ISSUES:
L185: `get_unchecked` with untrusted scanner `slot` → out-of-bounds read (UB)
L196: pointer into `buf` read after `extend_from_slice` may reallocate → use-after-free (UB)
L218: `from_utf8_unchecked` on untrusted network bytes → invalid `str` (UB)
L259: `confirm` locks `holds` then `warehouse`, the reverse of `place_hold`/`sweep_expired` → deadlock
L253: `Instant::now() + ttl` panics on overflow while holding both locks (and poisons them)
L81: `receive` replaces an existing item instead of adding qty; loses stock and resets `reserved`, orphaning holds
L120: `record_loss` unchecked `on_hand -= lost` underflows and can drop `on_hand` below `reserved`
L47: `on_hand - reserved` underflows once `reserved > on_hand` (panic in debug / huge value in release)
L112: `ship` doesn't check `on_hand`; `on_hand -= qty` can underflow
L127: `on_hand * price_cents` and the sum can overflow `u64`
L157: `prices[i + 1]` out of bounds on the last iteration → always panics for non-empty input
L204: `name.len() as u8` truncates names over 255 bytes → corrupt wire records
L266: hold is removed before `ship`; if `ship` fails the hold is lost with no rollback