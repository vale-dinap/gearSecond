Each section below explains one defect. The full list is at the end.

## Undefined behaviour (`unsafe`)

**`SlotTable::lookup` (L185).** `get_unchecked(slot)` takes `slot` straight from a scanner message. If `slot` is out of range, this is an out-of-bounds read, which is UB. It is not a panic. A hostile or buggy handheld can read arbitrary heap memory as an `Option<Sku>`. Use `self.slots.get(slot).copied().flatten()`. The bounds check costs nothing measurable.

**`append_batch` (L194–196).** `first` is a raw pointer into `buf`'s allocation. `extend_from_slice(tail)` may reallocate, and then `*first` reads freed memory, which is use-after-free UB. The value is already known (`head`), so return `Some((head, buf.len()))` and drop the pointer.

**`decode` (L218).** `from_utf8_unchecked` runs on bytes "received from the network". A `str` that is not valid UTF-8 breaks a language invariant, so any later string operation is UB. Use `std::str::from_utf8(...).map_err(|_| InvError::Malformed("bad utf-8"))?`.

## Panics, overflow and broken invariants

**`deltas` (L156–157).** The loop runs `i` up to `prices.len() - 1` and indexes `prices[i + 1]`. That index is out of bounds on the last iteration, so the function panics on every non-empty input. Loop to `prices.len().saturating_sub(1)`, or use `prices.windows(2).map(|w| w[1] - w[0])`. The `i64` subtraction can also overflow on extreme values. Consider `checked_sub` or `wrapping_sub` if inputs are untrusted.

**`record_loss` (L120).** There is no check that `lost <= on_hand`.
- Too large a `lost` underflows `on_hand`. That is a panic in debug and a wrap to ~4 billion units in release.
- Even when it doesn't underflow, it can push `on_hand` below `reserved`.

That breaks the `reserved <= on_hand` invariant everything else relies on. It should return `Insufficient` when `lost > on_hand`. It also needs a policy for reserved units, such as rejecting the loss or reducing `reserved` as well.

**`Item::available` (L47).** `on_hand - reserved` underflows once the invariant is broken, for example after `record_loss`. It panics in debug and in release reports a huge available count. That count lets `reserve` over-commit stock, and `low_stock` will miss the SKU. The same broken invariant also makes `ship`'s `on_hand -= qty` (L112) underflow.

**`total_value` (L127).** `on_hand as u64 * price_cents` and the `.sum()` can overflow `u64`, because `price_cents` is an unconstrained `u64`. That panics in debug and silently wraps in release. Use `checked_mul`/`checked_add` or `u128`, or bound prices.

**`place_hold` (L253).** `Instant::now() + ttl` panics if `ttl` is huge, for example `Duration::MAX` from a client-supplied value. Use `checked_add` and return an error.

## Logic errors

**`receive` (L80–81).** The doc says units are added for an existing SKU. Instead, `insert` replaces the whole `Item`. That discards existing `on_hand` and resets `reserved` to 0 while holds still reference those units. A later `confirm` → `ship` then fails, or a `release` silently does nothing. Use the entry API:
```rust
let item = self.items.entry(sku).or_insert_with(|| Item { sku, name: name.to_string(), on_hand: 0, reserved: 0, price_cents });
item.on_hand += qty; // checked_add if qty is untrusted
```

**`encode` (L204).** `name.len() as u8` truncates names of 256 bytes or more. The length prefix then disagrees with the payload. `decode` reads the wrong bytes as the name, sku and qty, and may split a UTF-8 code point. Combined with L218, that last case is UB. Reject or truncate long names explicitly, on a char boundary.

## Concurrency

**Lock-order inversion → deadlock (L259/L262/L265 vs L245/L247 and L272/L273).**
- `place_hold` and `sweep_expired` lock `warehouse` then `holds`.
- `confirm` locks `holds` then `warehouse`, and keeps `holds` locked while it takes `warehouse`.

A `confirm` running at the same time as `place_hold` or `sweep_expired` can deadlock both threads. Fix it by always taking `warehouse` first in `confirm`. Alternatively, remove the hold, drop the `holds` guard, then lock the warehouse. A single `Mutex` around both maps is the simplest option.

ISSUES:
L185: `get_unchecked` with untrusted scanner index — out-of-bounds read, UB
L196: raw pointer read after `extend_from_slice` may have reallocated — use-after-free, UB
L218: `from_utf8_unchecked` on network bytes — invalid `str`, UB
L157: `prices[i + 1]` out of bounds on last iteration — always panics for non-empty input
L120: `record_loss` unchecked subtraction — `on_hand` underflow, and can drop below `reserved`
L47: `on_hand - reserved` underflows once invariant broken — panic or huge bogus availability
L112: `on_hand -= qty` can underflow when `on_hand < reserved`
L127: `on_hand * price_cents` and sum can overflow u64
L81: `receive` replaces existing item instead of adding — loses stock and resets `reserved` under live holds
L204: `name.len() as u8` truncates long names — corrupt encoding and misparsed records
L259: `confirm` locks `holds` then `warehouse`, opposite order to `place_hold`/`sweep_expired` — deadlock
L253: `Instant::now() + ttl` panics on overflow for large TTL