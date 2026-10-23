I found several real defects. The most serious are a guaranteed panic in `deltas`, a lock-order deadlock between `confirm` and `place_hold`, and three `unsafe` blocks that take untrusted input.

**Panics and UB**

- **`deltas` (L157) always panics on non-empty input.** The loop runs `i` over `0..prices.len()`, so the last iteration reads `prices[len]`. It should iterate `0..len-1` or use `windows(2)`. The `i64` subtraction can also overflow for extreme prices.
- **`lookup` (L185) reads out of bounds.** `slot` comes from a scanner message, and `get_unchecked` does no check. Use `self.slots.get(slot).copied().flatten()`.
- **`append_batch` (L194–196) reads freed memory.** `first` points into `buf` before `extend_from_slice`, which can reallocate. Dereferencing `first` afterwards is a use-after-free. The value is always `head`, so `buf[start]` or just `head` is correct.
- **`decode` (L218) builds a `str` with `from_utf8_unchecked` on network bytes.** Invalid UTF-8 is UB. Use `std::str::from_utf8` and return `Malformed`.

**Arithmetic**

- **`available` (L47) underflows when `reserved > on_hand`.** This state is reachable through `record_loss`. It panics in debug builds and wraps in release, which makes `available()` return a huge number and lets `reserve` succeed.
- **`ship` (L112) and `record_loss` (L120) underflow `on_hand`.** `ship` only checks `qty` against `reserved`, and `record_loss` does not check at all. Both should validate against `on_hand` and return `Insufficient`.
- **`total_value` (L127) can overflow.** `on_hand as u64 * price_cents` and the sum are unchecked. Use `checked_mul`/`checked_add` or `saturating_*`.
- **`place_hold` (L253) panics on a large `ttl`.** `Instant + Duration` panics on overflow. Use `checked_add` and return an error.

**Logic and concurrency**

- **Deadlock (L259, with L245–247).** `place_hold` locks `warehouse` then `holds`. `confirm` locks `holds` then `warehouse` (L262, L265). Two threads running these concurrently can deadlock. `sweep_expired` uses the same order as `place_hold`, so `confirm` is the one to change. Take `warehouse` first, or finish with `holds` before touching `warehouse`.
- **`receive` (L81) overwrites existing SKUs.** The doc says units are added, but `insert` replaces the item and resets `on_hand` and `reserved`. Existing holds then point at stock that no longer exists. It should update `on_hand` with `saturating_add` when the SKU already exists.
- **`encode` (L204) truncates the length.** `name.len() as u8` wraps for names over 255 bytes, but the full name is still written, so the frame is corrupt. Reject long names, or check with `u8::try_from`.
- **`confirm` (L266) drops the hold when `ship` fails.** The hold is already removed, so its reservation is never released. This only happens if the invariant is already broken, but it leaves stock permanently reserved.

ISSUES:
L47: available() underflows when reserved > on_hand (reachable via record_loss)
L81: receive() overwrites an existing SKU, resetting on_hand and reserved instead of adding
L112: ship() checks qty against reserved only, so on_hand -= qty can underflow
L120: record_loss() subtracts without checking, can underflow and leave reserved > on_hand
L127: total_value() u32*u64 multiplication and sum can overflow
L157: deltas() indexes prices[i+1] for i up to len-1, out-of-bounds panic on any non-empty input
L185: lookup() get_unchecked on scanner-supplied slot, out-of-bounds UB
L196: append_batch() dereferences pointer invalidated by extend_from_slice reallocation, use-after-free
L204: encode() truncates name length to u8 for names over 255 bytes, corrupt frame
L218: decode() from_utf8_unchecked on untrusted bytes, UB on invalid UTF-8
L253: place_hold() Instant + ttl panics on overflow for very large Duration
L259: confirm() locks holds then warehouse, inverse of place_hold order, deadlock
L266: confirm() drops hold when ship fails, leaving its reservation permanently held