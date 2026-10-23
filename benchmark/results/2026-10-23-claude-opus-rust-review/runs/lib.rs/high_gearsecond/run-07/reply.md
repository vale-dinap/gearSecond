# Review of `src/lib.rs`

The module has two memory-safety bugs reachable from untrusted input, one use-after-realloc, a lock-order deadlock, and several arithmetic and logic errors that can panic in debug builds or corrupt stock counts in release builds.

## Undefined behaviour / memory safety

**L185, `SlotTable::lookup`: unchecked index on untrusted input.**
The doc comment says `slot` comes straight from a handheld scanner message. `get_unchecked` with an out-of-range index is immediate UB: an out-of-bounds read that a malicious or buggy scanner can trigger. Use `self.slots.get(slot).copied().flatten()`. The bounds check costs almost nothing.

**L194–196, `append_batch`: dangling pointer read.**
`first` is taken from `buf.as_ptr()` before `extend_from_slice`. If the extend reallocates, `first` points into freed memory and `*first` is a use-after-free. The value is `head` anyway, so return `head` directly or read `buf[start]` after extending.

**L218, `decode`: `from_utf8_unchecked` on network bytes.**
Creating a `str` from invalid UTF-8 is UB, and this buffer comes from the network. Use `std::str::from_utf8(&rest[..len]).map_err(|_| InvError::Malformed("name not utf-8"))?`.

## Concurrency

**L245/247 vs L259/262/265: lock-order inversion, which deadlocks.**
`place_hold` and `sweep_expired` lock `warehouse` then `holds`. `confirm` locks `holds` and then, while still holding it, locks `warehouse`. A `confirm` running at the same time as a `place_hold` or `sweep_expired` can deadlock. Fix it by acquiring locks in one consistent order everywhere. Alternatively, drop `holds` in `confirm` before touching `warehouse`, since the hold has already been removed.

## Logic errors

**L80–81, `receive`: overwrites existing stock.**
The doc says units are added for an existing SKU. Instead, `insert` replaces the whole `Item`, which discards prior `on_hand` and resets `reserved` to 0. Outstanding holds then point at stock that no longer counts as reserved. Later `ship`/`release` calls on those holds either fail or ship unreserved units. Use `entry(sku)` and add `qty` with checked or saturating addition when the SKU exists.

**L120, `record_loss`: unchecked subtraction, and the invariant can break.**
- If `lost > on_hand`, `on_hand -= lost` panics in debug and wraps to a huge value in release.
- Even without underflow, it can push `on_hand` below `reserved`, which breaks the invariant that other methods rely on:
  - `available()` at **L47** then underflows (panic in debug, or a huge "available" count in release that allows over-reservation).
  - `ship` at **L112** can underflow `on_hand`.

  Validate `lost <= on_hand`. Also decide whether losses reduce reservations, or clamp them.

**L157, `deltas`: out-of-bounds panic.**
The loop runs `i` over `0..len`, so the last iteration indexes `prices[len]` and always panics for non-empty input. It should be `0..prices.len().saturating_sub(1)`, or use `prices.windows(2)`. The `i64` subtraction can also overflow for extreme values; `checked_sub` or `wrapping_sub` makes the intent explicit.

## Integer overflow / truncation

**L127, `total_value`: `on_hand as u64 * price_cents` and `.sum()` can overflow.**
A `u32` quantity times an arbitrary `u64` price easily exceeds `u64::MAX`. That panics in debug and silently wraps in release. Use `checked_mul`/`checked_add` and return an `Option`/`Result`, or accumulate in `u128`.

**L204, `encode`: `name.len() as u8` truncates.**
For names of 256 bytes or more, the length prefix wraps, but all name bytes are still written. The record becomes undecodable or decodes to garbage SKU and quantity values. Reject or truncate long names, ideally at a UTF-8 char boundary.

**L253, `place_hold`: `Instant::now() + ttl` panics on overflow.**
A very large caller-supplied `ttl` panics. The `reserve` at L246 has already happened by then, so the panic leaks the reservation and also poisons both mutexes. Use `checked_add` and compute it before reserving.

ISSUES:
L185: get_unchecked with scanner-supplied slot index is UB (out-of-bounds read)
L196: pointer taken before extend_from_slice may dangle after reallocation; use-after-free read
L218: from_utf8_unchecked on untrusted network bytes is UB
L259: confirm locks holds then warehouse while place_hold/sweep_expired lock warehouse then holds; deadlock
L81: receive overwrites existing item, losing on_hand and resetting reserved instead of adding units
L120: record_loss subtraction can underflow and can drop on_hand below reserved
L47: available() underflows when on_hand < reserved (reachable via record_loss)
L112: ship's on_hand -= qty can underflow once on_hand < reserved
L157: deltas loop indexes prices[i + 1] past the end; always panics on non-empty input
L127: on_hand * price_cents and the sum can overflow u64
L204: name.len() as u8 truncates for names >= 256 bytes, corrupting the record
L253: Instant::now() + ttl can panic on large ttl after the stock is already reserved