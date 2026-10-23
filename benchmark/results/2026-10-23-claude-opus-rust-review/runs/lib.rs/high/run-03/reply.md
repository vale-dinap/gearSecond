# Review of `src/lib.rs` (inventory service)

The module has four memory-safety bugs (undefined behaviour) in safe-looking public functions, a deadlock in `Service`, and several logic and arithmetic defects that corrupt stock or panic. I reviewed this by reading the code only; I did not compile or run it.

## Undefined behaviour

**`SlotTable::lookup` (L185).** `get_unchecked(slot)` runs on an index that, per the doc comment, "comes straight from a handheld scanner message". Any `slot >= slots.len()` reads out of bounds, which is UB in a safe `pub fn`. A bounds check costs almost nothing here.
- Fix: `self.slots.get(slot).copied().flatten()`.

**`append_batch` (L194–L196).** `first` is a raw pointer into `buf`'s heap buffer. `extend_from_slice(tail)` may reallocate, which frees that buffer. `*first` is then a use-after-free read.
- Fix: drop the pointer and return `head`, or read `buf[start]` after extending.

**`decode` (L218).** `from_utf8_unchecked` is called on bytes "received from the network". A `String` holding invalid UTF-8 is UB and can break later string operations.
- Fix: `std::str::from_utf8(&rest[..len]).map_err(|_| InvError::Malformed("bad utf-8"))?`.

**`encode` (L204).** `name.len() as u8` silently truncates names longer than 255 bytes. The record then decodes as the wrong name with garbage SKU and quantity. The truncation can also split a multi-byte character, which combined with L218 produces a non-UTF-8 `String`.
- Fix: reject long names (return `Result`) or use a wider length prefix.

## Concurrency

**Deadlock from inconsistent lock order (L259 vs L245/L247 and L272/L273).**
- `place_hold` and `sweep_expired` lock `warehouse` and then `holds`.
- `confirm` locks `holds` and then `warehouse` (L262/L265) while still holding `holds`.
- If `confirm` runs at the same time as either of the other two, each thread can hold one lock and wait on the other forever.
- Fix: always take `warehouse` before `holds`.

**`place_hold` (L253).** `Instant::now() + ttl` panics if a caller passes a huge `ttl` (e.g. `Duration::MAX`). At that point the stock is already reserved (L246), so the reservation leaks. Both mutexes are also poisoned, so every later `lock().unwrap()` panics and the service is dead.
- Fix: use `Instant::now().checked_add(ttl)` and fail before reserving.

## Logic and arithmetic

**`receive` (L80–L81).** The doc says units are added to an existing SKU. The code instead `insert`s a fresh `Item`, which:
- throws away the current `on_hand`;
- resets `reserved` to 0 while holds are still outstanding, so a later `confirm` → `ship` fails with `Insufficient` after the hold has already been removed.

Fix: use the entry API and add the quantity. Use `checked_add` to avoid overflow.

**`record_loss` (L120).** `on_hand -= lost` has no check:
- If `lost > on_hand`, it panics in debug builds and wraps to roughly 4 billion units in release builds.
- Even when it doesn't underflow, it can leave `on_hand < reserved`, which breaks the invariant everything else relies on.

Fix: validate `lost` against `on_hand`, and decide what happens to reserved units when `on_hand` drops below `reserved`.

**`Item::available` (L47).** `on_hand - reserved` underflows once `reserved > on_hand`, which L120 makes reachable. This panics, or wraps in release builds:
- `reserve` would then see huge availability and over-reserve;
- `ship` (L112) can underflow `on_hand` the same way.

When this happens inside `Service`, the panic also poisons the mutex.

**`total_value` (L127).** `on_hand as u64 * price_cents` and the `.sum()` are unchecked. `price_cents` is an arbitrary `u64`, so overflow is reachable: it panics in debug and returns a wrong total in release.
- Fix: use `checked_mul`/`checked_add` (returning `Option`), or accumulate in `u128`.

**`deltas` (L156–L157).** The loop runs `i` over `0..len` and reads `prices[i + 1]`. That indexes past the end on the last iteration, so it panics for every non-empty input.
- Fix: iterate `prices.windows(2)`.
- Separately, `b - a` on `i64` can overflow for extreme values; consider `checked_sub`.

ISSUES:
L80: `receive` overwrites an existing SKU instead of adding units, losing on-hand stock and resetting `reserved` under live holds
L120: `record_loss` uses unchecked `on_hand -= lost` (underflow panic or wrap) and can drop `on_hand` below `reserved`
L47: `available()` underflows when `reserved > on_hand`, panicking or wrapping to a huge value
L127: `total_value` multiplication and sum can overflow `u64`
L157: `deltas` reads `prices[i + 1]` past the end, panicking for any non-empty input
L185: `get_unchecked` with an untrusted scanner index is out-of-bounds UB
L196: raw pointer read after `extend_from_slice` may have reallocated `buf` is a use-after-free UB
L204: name length truncated to `u8` for names over 255 bytes, producing corrupt records
L218: `from_utf8_unchecked` on network data creates a `String` with invalid UTF-8 (UB)
L259: `confirm` locks `holds` then `warehouse`, the reverse of `place_hold`/`sweep_expired`, which can deadlock
L253: `Instant::now() + ttl` panics on overflow after the stock is reserved, leaking the reservation and poisoning the mutexes