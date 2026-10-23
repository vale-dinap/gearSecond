Review below, roughly ordered by severity.

## Undefined behaviour (unsafe misuse)

**`SlotTable::lookup` (L185)**: `get_unchecked(slot)` is called with an index the doc comment says "comes straight from a handheld scanner message". Any out-of-range slot is an out-of-bounds read, which is UB. That is a memory-safety hole reachable from untrusted input. Use `self.slots.get(slot).copied().flatten()`. The bounds check costs almost nothing.

**`append_batch` (L194–196)**: `first` is a raw pointer into `buf`'s allocation taken *before* `extend_from_slice`. If the extend reallocates, `first` dangles and `*first` is a use-after-free read. `wrapping_add` does not help. Read `buf[start]` after the extend, or just return `head`, which already holds that value.

**`decode` (L218)**: `from_utf8_unchecked` runs on bytes "received from the network". Creating a `str` with invalid UTF-8 is UB. Use `std::str::from_utf8(..).map_err(|_| InvError::Malformed("bad utf-8"))?`.

## Concurrency

**Lock-order inversion / deadlock (L245–247 vs L259, L262/L265)**: `place_hold` and `sweep_expired` lock `warehouse` then `holds`. `confirm` locks `holds` and, while still holding it, locks `warehouse`. If `confirm` runs concurrently with either of the others, each thread can end up holding one lock and waiting on the other. Pick a single order (warehouse → holds) everywhere. Alternatively, in `confirm`, remove the hold and drop the `holds` guard before taking `warehouse`.

## Logic errors

**`Warehouse::receive` (L80–81)**: The doc says units are added to an existing SKU, but `insert` replaces the whole `Item`. That discards the existing `on_hand` and resets `reserved` to 0 while holds still reference that stock. Use `entry(sku).and_modify(|i| i.on_hand += qty).or_insert(...)`, preferably with `checked_add`.

**`deltas` (L156–157)**: The loop runs `i` up to `len - 1` and indexes `prices[i + 1]`, so it panics on every non-empty input. Iterate `0..prices.len().saturating_sub(1)` or use `prices.windows(2)`. The subtraction can also overflow for extreme `i64` values. Use `checked_sub` or widen to `i128` if that matters.

## Integer overflow / panics

**`record_loss` (L120)**: `on_hand -= lost` has no check. It panics in debug and wraps to ~4 billion in release when `lost > on_hand`. It also never checks against `reserved`, so it can leave `on_hand < reserved`. That breaks the invariant everything else relies on:
- **L47 `available()`**: `on_hand - reserved` then underflows. It panics in debug or reports huge availability in release, which lets `reserve` oversell. `low_stock` (L132) also calls this.
- **L112 `ship`**: `on_hand -= qty` only checks `qty <= reserved`, so it underflows in the same broken-invariant state.

Validate `lost <= on_hand` in `record_loss` and decide policy for reserved units, e.g. return an error or clamp `reserved`. Also make `available()` use `saturating_sub` defensively.

**`total_value` (L127)**: `on_hand as u64 * price_cents` and the `sum()` can overflow `u64` with large prices. Use `checked_mul`/`checked_add` or accumulate in `u128`.

**`encode` (L204)**: `name.len() as u8` silently truncates names longer than 255 bytes. The length prefix then disagrees with the bytes written, so `decode` misreads the SKU and quantity from the middle of the name. Reject or truncate long names explicitly. `receive` does not limit name length.

**`place_hold` (L253)**: `Instant::now() + ttl` panics on overflow if a caller passes a very large `ttl`, such as `Duration::MAX`. Use `checked_add` and return an error.

ISSUES:
L185: get_unchecked on untrusted scanner index, out-of-bounds read is UB
L194: raw pointer into Vec held across extend_from_slice, dangling after realloc, use-after-free at L196
L218: from_utf8_unchecked on network bytes, invalid UTF-8 is UB
L259: confirm locks holds then warehouse while place_hold/sweep_expired lock warehouse then holds, deadlock
L81: receive overwrites existing item, losing on_hand and resetting reserved instead of adding stock
L157: deltas indexes prices[i + 1] past end, panics on any non-empty input; subtraction can overflow
L120: record_loss subtracts without checking, underflows and can leave on_hand < reserved
L47: available() underflows when on_hand < reserved, panic or wrap enables overselling
L112: ship's on_hand -= qty can underflow once invariant is broken
L127: on_hand * price_cents and sum can overflow u64
L204: name.len() as u8 truncates names > 255 bytes, producing corrupt records
L253: Instant::now() + ttl panics on overflow for very large ttl