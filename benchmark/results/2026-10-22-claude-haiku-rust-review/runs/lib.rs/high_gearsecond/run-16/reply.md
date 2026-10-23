## Defects in `src/lib.rs`

I read the code but did not compile or run it, so these come from inspection only. The most serious are the undefined behaviour in `lookup` and `append_batch`, the out-of-bounds panic in `deltas`, and the lock-order deadlock between `confirm` and `place_hold`/`sweep_expired`.

### Memory safety and undefined behaviour

- **`lookup` (L185)** calls `get_unchecked` on a slot index that comes from a scanner message. Any slot ≥ `slots.len()` is out-of-bounds UB. The "hot path" comment does not justify skipping the check. Use `self.slots.get(slot).copied().flatten()`.
- **`append_batch` (L194–197)** takes a raw pointer into `buf`, then calls `extend_from_slice`, which can reallocate. The read at L196 then dereferences a dangling pointer, which is use-after-free. The function is also pointless: the value read is just `head`, so `Some((head, buf.len()))` is correct.
- **`decode` (L218)** calls `from_utf8_unchecked` on bytes from the network. Invalid UTF-8 produces a `String` that violates its invariant, which is UB. Use `std::str::from_utf8` and map the error to `InvError::Malformed`.

### Panics and overflow

- **`deltas` (L156–157)** loops over `0..prices.len()` but reads `prices[i + 1]`. On the last iteration that index is `len`, so every non-empty input panics. Use `prices.windows(2).map(|w| w[1] - w[0])`, which also avoids the `i64` subtraction going unchecked (it can overflow for extreme values).
- **`available` (L47)** computes `on_hand - reserved`. `record_loss` can make `on_hand < reserved`, so this underflows: a panic in debug builds and a wrap in release builds. `low_stock` (L132) inherits the same problem.
- **`ship` (L111–112)** and **`record_loss` (L120)** subtract without checks. `record_loss` accepts any `lost`, even more than `on_hand`, and does not clamp `reserved`, which leaves the invariant `reserved <= on_hand` broken. A later `ship` then underflows `on_hand`.
- **`total_value` (L127)** multiplies `u32 as u64` by `u64` price and sums the results unchecked. Both can overflow. Use `checked_mul`/`checked_add` or `saturating_*`.
- **`place_hold` (L253)** computes `Instant::now() + ttl`, which panics if the sum overflows (for example with a very large `Duration`). Use `checked_add` and return an error.

### Logic errors

- **`receive` (L80–81)** does not add to existing stock, although its doc comment says it should. It replaces the whole `Item`, which resets `reserved` to 0 while holds for that SKU still exist. That allows overcommit, and the later `ship` then underflows. It also silently overwrites the name and price. It should update `on_hand` in place when the SKU exists.
- **`release` (L101)** uses `saturating_sub`, so releasing more than is reserved silently frees units that belong to other holds. It should return an error on over-release, as `ship` does.
- **`encode` (L204)** does `name.len() as u8`. A name longer than 255 bytes gets its length truncated, while all of its bytes are still written, so the frame is corrupt and the decoder misreads everything after it. Reject names over 255 bytes, or truncate at a char boundary and document it.
- **`confirm` (L260–266)** removes the hold from the map before calling `ship`. If `ship` fails, the hold is gone and the caller gets an error with no hold to retry. Remove it only after success, or reinsert it on failure.

### Concurrency

- **Lock-order inversion (deadlock).** `place_hold` (L245, then L247) and `sweep_expired` (L272, then L273) take `warehouse` before `holds`. `confirm` (L259, then L262/L265) takes `holds` before `warehouse`. If one thread is in `confirm` while another is in `place_hold` or `sweep_expired`, each can hold one lock and wait for the other. Pick one order and use it everywhere, or hold a single mutex around both structures.
- **Mutex poisoning** is handled by `unwrap()` everywhere, so one panic in any critical section makes every later call panic. This is a robustness issue rather than a bug on its own, but it compounds the panics above.

The tests (L315–335) cover only the happy path, so none of the defects above is exercised.

ISSUES:
L47: available() underflows when reserved > on_hand (panic in debug, wrap in release); also breaks low_stock
L80: receive() replaces the existing Item instead of adding to on_hand; resets reserved to 0 while holds exist
L101: release() saturating_sub silently frees units belonging to other holds
L111: ship() on_hand -= qty underflows when on_hand < reserved
L120: record_loss() has no bound on lost; on_hand underflows and reserved is not clamped
L127: total_value() u64 multiply and sum can overflow
L157: deltas() reads prices[i + 1] past the end on last iteration; panics for any non-empty input
L185: lookup() get_unchecked on untrusted scanner slot; out-of-bounds UB
L194: append_batch() raw pointer dangles after extend_from_slice reallocates; deref is UB
L204: encode() name.len() as u8 truncates names over 255 bytes; corrupt frame
L218: decode() from_utf8_unchecked on network bytes; UB on invalid UTF-8
L245: place_hold() locks warehouse then holds; inverse of confirm() order; deadlock risk
L253: place_hold() Instant + ttl panics on overflow; use checked_add
L259: confirm() locks holds then warehouse; inverse of place_hold()/sweep_expired() order; deadlock risk
L260: confirm() removes hold before ship(); ship failure drops the hold with no retry
L272: sweep_expired() locks warehouse then holds; inverse of confirm() order; deadlock risk