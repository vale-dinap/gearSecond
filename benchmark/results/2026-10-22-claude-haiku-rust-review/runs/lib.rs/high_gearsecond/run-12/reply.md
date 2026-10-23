## Defects

**Undefined behaviour and memory safety**

- **`SlotTable::lookup` (L185)** calls `get_unchecked` on `slot`, which the doc comment says comes straight from a scanner message. Any out-of-range slot is an out-of-bounds read. Use `self.slots.get(slot).copied().flatten()`.
- **`append_batch` (L194-197)** takes `first` as a raw pointer into `buf` before `extend_from_slice`. The extend can reallocate, leaving `first` dangling, and the dereference at L196 is a use-after-free. The value is just `head`, so return `head` and drop the pointer entirely.
- **`decode` (L218)** calls `from_utf8_unchecked` on bytes from the network. Invalid UTF-8 is immediate UB. Use `std::str::from_utf8` and map the error to `Malformed`.

**Integer overflow and underflow**

- **`record_loss` (L120)** does `on_hand -= lost` unchecked, so `lost > on_hand` panics in debug and wraps in release. It also lets `on_hand` drop below `reserved`, which breaks the invariant that `available()` (L47) and `ship` (L112) rely on. Check `lost <= on_hand - reserved` and return an error.
- **`total_value` (L127)** does `on_hand as u64 * price_cents` and then `sum()`, both unchecked. Use `checked_mul` and `checked_add`, or saturate.
- **`deltas` (L157)** subtracts `i64` values unchecked, so extreme prices overflow. Use `checked_sub`.
- **`place_hold` (L253)** does `Instant::now() + ttl`, which panics for a large `Duration`. Use `checked_add` and return an error.

**Logic errors**

- **`receive` (L80-81)** uses `insert`, which replaces an existing SKU. The doc says units are added, but `on_hand` is set to `qty` and `reserved` is reset to 0. Outstanding holds then point at reservations that no longer exist, so `confirm` fails. Update the existing entry instead.
- **`encode` (L204)** casts `name.len()` to `u8` without a check. A name over 255 bytes produces a length byte that disagrees with the payload, so the frame is corrupt. Return an error for names over 255 bytes.
- **`confirm` (L265-266)** removes the hold at L260 before shipping. If `ship` fails (for example after the overwrite above), the hold is lost and the units are never released. Ship first, or restore the hold on failure.
- **`moving_average` (L143)** asserts on `window == 0`, so bad input from a caller panics. That may be intended, but it is worth a documented `Result` if callers are untrusted.

**Concurrency**

- **Lock-order inversion.** `place_hold` (L245, then L247) and `sweep_expired` (L272, then L273) lock `warehouse` before `holds`. `confirm` (L259, then L265) locks `holds` before `warehouse`. If one thread is in `confirm` and another in `place_hold` or `sweep_expired`, they can deadlock. Pick one order everywhere, for example `warehouse` then `holds`, and make `confirm` follow it by taking the warehouse lock first.

Nothing else I checked is a defect. `moving_average` handles `window > len` correctly, the `saturating_sub` in `release` is intentional, and the `decode` length check at L215 is sound.

ISSUES:
L47: available() underflows when on_hand < reserved, reachable via record_loss
L80: receive replaces existing SKU, losing on_hand/reserved and orphaning holds
L120: record_loss unchecked subtraction, can underflow and break reserved <= on_hand
L127: total_value u64 multiply and sum can overflow
L157: deltas i64 subtraction can overflow
L185: get_unchecked on scanner-supplied slot, out-of-bounds UB
L196: raw pointer read after extend_from_slice may reallocate, use-after-free
L204: name length truncated to u8 without check, corrupt frame
L218: from_utf8_unchecked on network bytes, UB on invalid UTF-8
L253: Instant + ttl panics on large Duration
L259: confirm locks holds before warehouse, inverse of place_hold/sweep order, deadlock
L266: confirm removes hold before ship, lost hold if ship fails