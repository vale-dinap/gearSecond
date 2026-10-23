Most serious problems are unsafe code and undefined behaviour, followed by a lock-order deadlock and a stock-accounting bug that can oversell.

**Undefined behaviour (fix before merge)**

- **`SlotTable::lookup` (L185):** `get_unchecked` runs on a slot index from a scanner message. Any out-of-range value is an out-of-bounds read. Use `self.slots.get(slot).copied().flatten()`. The "hot path" comment doesn't justify it.
- **`append_batch` (L194–197):** `first` is a raw pointer taken before `extend_from_slice`. The extend can reallocate `buf`, so `*first` reads freed memory. The pointer is also unnecessary: the head value is already available as `head`, so return `Some((head, buf.len()))`.
- **`decode` (L218):** `from_utf8_unchecked` runs on bytes from the network. Invalid UTF-8 is immediate UB. Use `std::str::from_utf8` and map the error to `Malformed`.

**Panics and overflow**

- **`deltas` (L156–157):** the loop runs `i` over `0..prices.len()` and reads `prices[i + 1]`. On the last iteration that is `prices[len]`, so any non-empty input panics. The range should be `0..prices.len() - 1` (or use `windows(2)`). The subtraction can also overflow `i64` for extreme prices; `checked_sub` or `i128` would cover it.
- **`Item::available` (L47):** `on_hand - reserved` underflows whenever `reserved > on_hand`. That state is reachable (see below). In debug it panics. In release it wraps to a huge value, so `reserve` accepts oversells.
- **`record_loss` (L120) and `ship` (L112):** both subtract from `on_hand` without checking it. `record_loss` can push `on_hand` below `reserved`, which breaks the invariant `available()` depends on. A later `ship` then underflows.
- **`total_value` (L127):** `on_hand as u64 * price_cents` and the `sum` can overflow `u64`. Use `checked_mul`/`checked_add` or saturate.
- **`place_hold` (L253):** `Instant::now() + ttl` panics when `ttl` is very large. Use `checked_add` and return an error.

**Logic errors**

- **`receive` (L81):** `insert` replaces the whole entry. The doc at L77–78 says units are added to existing stock, but the code sets `on_hand = qty` and resets `reserved` to 0. Outstanding holds stay live while their reservation is gone, so stock is overcommitted. Fix: update the existing item with `on_hand += qty` and keep `reserved`.
- **`confirm` (L260–266):** the hold is removed before `ship` runs. If `ship` fails (for example, `reserved` is short because of the bug above), the hold is gone and its units are never released. Ship first, or re-insert the hold on failure.
- **`encode` (L204):** `name.len() as u8` silently truncates names over 255 bytes. The length prefix then disagrees with the payload, and the record is corrupt. Reject long names instead.

**Concurrency**

- **Lock-order inversion:** `place_hold` (L245, then L247) and `sweep_expired` (L272, then L273) take `warehouse` then `holds`. `confirm` (L259, then L262/L265) takes `holds` then `warehouse`. Two threads, one in `confirm` and one in `place_hold` or `sweep_expired`, can deadlock. Pick one global order and use it everywhere. Holding `holds` across the warehouse call in `confirm` is the usual culprit.

**Checked, no defect found**

- `moving_average`: the window bounds are correct, and the empty result for `window > len` is intended.
- `decode`: the length check covers the `try_into().unwrap()` calls, so those can't panic.
- `reserve_and_ship` and `codec_round_trip` tests: the expected values match the code.

The `ISSUES:` list below covers the defects above.

ISSUES:
L47: available() underflows when reserved > on_hand; wraps in release, allowing oversell
L81: receive() replaces the entry, resetting reserved and on_hand instead of adding stock
L112: ship() subtracts from on_hand unchecked; underflows if on_hand < reserved
L120: record_loss() subtracts unchecked; can drop on_hand below reserved
L127: total_value() u64 multiplication and sum can overflow
L157: deltas() reads prices[len] on the last iteration, panicking on any non-empty input
L185: lookup() uses get_unchecked on untrusted scanner slot index; out-of-bounds UB
L196: append_batch() reads through pointer invalidated by extend reallocation; use-after-free UB
L204: encode() truncates names over 255 bytes with `as u8`, corrupting the record
L218: decode() uses from_utf8_unchecked on network input; UB on invalid UTF-8
L253: place_hold() Instant::now() + ttl panics on very large ttl
L259: confirm() locks holds before warehouse; inverts order used by place_hold/sweep_expired; deadlock risk
L266: confirm() removes hold before ship(); on failure the hold and its units are lost