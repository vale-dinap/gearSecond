I found 13 real defects. Five are memory-safety, crash or deadlock problems, so this shouldn't merge as-is.

## Critical: undefined behaviour and memory safety

**L185 – `SlotTable::lookup` uses `get_unchecked` on untrusted input.** The doc comment says `slot` comes straight from a handheld scanner. Any out-of-range value is an out-of-bounds read, which is undefined behaviour. A bounds check is cheap. Use `self.slots.get(slot).copied().flatten()`.

**L194–196 – `append_batch` reads through a dangling pointer.** `first` is taken from `buf.as_ptr()` after the `push`. `extend_from_slice(tail)` can then reallocate `buf`, so `*first` may read freed memory. No pointer is needed here: return `head`, or read `buf[start]` after the extend.

**L218 – `decode` calls `from_utf8_unchecked` on network bytes.** A `str` holding invalid UTF-8 is undefined behaviour, and here the input is attacker-controlled. Use `std::str::from_utf8(...).map_err(|_| InvError::Malformed("bad utf-8"))?`.

## Concurrency

**L259 vs L245/L247 (also L272/L273) – lock-order inversion causes deadlock.** The two paths take the same locks in opposite orders:
- `place_hold` and `sweep_expired` lock `warehouse`, then `holds`.
- `confirm` locks `holds` (L259), then `warehouse` (L262/L265) while still holding `holds`.

If `confirm` runs at the same time as `place_hold` or `sweep_expired`, each thread can end up waiting on the other forever. Fix: use one global lock order (warehouse → holds → next_id) in `confirm` too, or put the state under a single mutex.

**L253 – `Instant::now() + ttl` can panic.** It panics on overflow, so a caller-supplied huge `ttl` (e.g. `Duration::MAX`) crashes the thread and poisons the `warehouse` and `holds` mutexes. Every later `.lock().unwrap()` then panics. Use `checked_add` and return an error.

## Logic errors

**L80–81 – `receive` overwrites existing stock.** The doc says units are added to an existing SKU. Instead, `insert` replaces the whole `Item`, which:
- discards the current `on_hand`;
- resets `reserved` to 0 while holds still reference those reservations.

A later `confirm` of such a hold then fails in `ship` with `Insufficient`, after the hold has already been removed. Use the `entry` API and add `qty` to `on_hand` for existing SKUs.

**L156–157 – `deltas` always panics on non-empty input.** The loop runs `i` up to `len - 1`, so `prices[i + 1]` indexes out of bounds on the last iteration. It should be `for i in 1..prices.len() { prices[i] - prices[i-1] }`, or use `prices.windows(2)`. The subtraction can also overflow `i64` for extreme values; use `checked_sub` or `wrapping_sub` if that matters.

**L204 – `encode` silently truncates long names.** `name.len() as u8` wraps for names of 256 bytes or more. The length prefix is then wrong and the record decodes as garbage. It can also split a multi-byte UTF-8 sequence. Reject such names, or widen the length field.

## Integer underflow and overflow

These panic in debug builds and wrap silently in release builds.

**L120 – `record_loss` doesn't validate `lost`.**
- If `lost > on_hand`, `on_hand -= lost` underflows.
- Even without underflow, it can push `on_hand` below `reserved`, which breaks the invariant `reserved <= on_hand` that the rest of the code relies on.

It should check against `on_hand` and decide what happens to reservations that can no longer be met.

**L47 – `available` underflows.** `on_hand - reserved` underflows once that invariant is broken (via L120 or L80). `low_stock` and `reserve` both call it.

**L112 – `ship` can underflow.** `item.on_hand -= qty` underflows if `on_hand < reserved`, for the same reason. It only checks `qty <= reserved`, not `qty <= on_hand`.

**L127 – `total_value` can overflow.** Both the per-item product `on_hand as u64 * price_cents` and the `sum` can overflow, because `price_cents` is an unbounded `u64`. Use `checked_mul`/`checked_add`, or `u128`.

## Minor

**L101 – `release` hides caller bugs.** `saturating_sub` silently accepts releasing more than is reserved. Returning `Insufficient` would surface the bug instead.

## Tests

The current tests don't cover any of these paths. Worth adding:
- `deltas` with at least one element;
- `receive` called twice on the same SKU;
- `decode` with invalid UTF-8;
- `append_batch` where the buffer has to grow;
- a concurrent `confirm`/`place_hold` stress test.

ISSUES:
L185: `get_unchecked` with untrusted scanner-supplied slot index is out-of-bounds UB
L196: pointer into `buf` read after `extend_from_slice` may have reallocated (use-after-free)
L218: `from_utf8_unchecked` on network data is UB for invalid UTF-8
L259: `confirm` locks holds then warehouse, the reverse of place_hold/sweep_expired, so it can deadlock
L253: `Instant::now() + ttl` panics on overflow with a huge ttl and poisons the mutexes
L81: `receive` overwrites an existing item, losing on_hand and resetting reserved instead of adding qty
L157: `deltas` indexes `prices[i + 1]` out of bounds on the last iteration (always panics for non-empty input)
L204: `name.len() as u8` truncates names of 256+ bytes, producing corrupt records
L120: `record_loss` subtracts without checks: underflow, and can drop on_hand below reserved
L47: `on_hand - reserved` underflows once on_hand < reserved
L112: `ship` subtracts from on_hand without checking it, so it can underflow
L127: `on_hand * price_cents` and the sum can overflow u64
L101: `release` silently saturates when releasing more than is reserved, masking caller errors