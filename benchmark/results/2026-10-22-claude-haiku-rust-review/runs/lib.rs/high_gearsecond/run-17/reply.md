## Defects

**Panics**

- **`deltas` (L156-157) panics on every non-empty input.** The loop runs `i` over `0..prices.len()`, so `prices[i + 1]` reads one past the end on the last iteration. Iterate `0..prices.len() - 1` or use `prices.windows(2)`. The `i64` subtraction can also overflow for extreme prices, so `checked_sub` is worth considering.
- **`available()` (L47) underflows when `reserved > on_hand`.** This panics in debug builds and wraps in release. It can happen: `record_loss` (L120) lowers `on_hand` without checking reservations.
- **`record_loss` (L120) and `ship` (L112) subtract without checks.** `lost > on_hand` underflows. `ship` is safe only while the `reserved <= on_hand` invariant holds, and `record_loss` breaks it.
- **`place_hold` (L253) panics on overflow.** `Instant::now() + ttl` panics for a large `Duration`. Use `checked_add` and return an error.

**Undefined behaviour**

- **`SlotTable::lookup` (L185) reads out of bounds.** `get_unchecked` on `slot`, which comes from a scanner message, is UB for any `slot >= len`. Use `self.slots.get(slot).copied().flatten()`. The "hot path" saving is not worth it here.
- **`append_batch` (L194-197) is a use-after-free.** `first` is a raw pointer into `buf`, taken before `extend_from_slice`. That call can reallocate, so `*first` reads freed memory. The value is `head`, already in hand, so the pointer and the `unsafe` block are unnecessary.
- **`decode` (L218) skips UTF-8 validation on network input.** `from_utf8_unchecked` on untrusted bytes is UB if they are invalid. Use `std::str::from_utf8` and map the error to `Malformed`.

**Data corruption**

- **`encode` (L204) truncates long names.** `name.len() as u8` wraps for names over 255 bytes, so the length prefix disagrees with the payload and the frame is corrupt. Reject long names with an error.
- **`receive` (L80-81) overwrites existing stock.** The doc says units are added, but `insert` replaces the item. `on_hand` is set to `qty` and `reserved` is reset to 0 while holds still exist. Confirmations then fail or ship against the wrong count.
- **`release` (L101) clamps silently.** `saturating_sub` hides releasing more than was reserved, which hides the same accounting bug.

**Overflow**

- **`total_value` (L127) can overflow.** `on_hand as u64 * price_cents` and the `sum` can exceed `u64::MAX`. Use `checked_mul` and `checked_add`, or `u128`.

**Concurrency**

- **Lock-order inversion (L259-262 vs L245-247, L272-273) can deadlock.** `confirm` takes `holds` then `warehouse`. `place_hold` and `sweep_expired` take `warehouse` then `holds`. Two threads can each hold one lock and wait for the other. Pick one order everywhere.
- **Poisoned locks cascade.** Each `lock().unwrap()` turns one panic into a panic in every later caller. Consider `unwrap_or_else(|e| e.into_inner())` if the state is still usable after a panic.

**Logic**

- **Expired holds keep stock blocked until `sweep_expired` runs.** Nothing in this module calls it, so `reserve` fails on stock that should be free. Schedule the sweep, or check expiry in `place_hold`.

ISSUES:
L156: deltas off-by-one, prices[i + 1] indexes past end, panics on any non-empty input
L157: i64 subtraction can overflow for extreme prices
L47: available() underflows when reserved > on_hand, panics in debug
L120: record_loss subtracts without check, underflows when lost > on_hand
L112: ship subtracts on_hand without check, underflows if invariant broken
L127: on_hand as u64 * price_cents and sum can overflow
L185: get_unchecked on untrusted slot index, out-of-bounds read (UB)
L196: dangling pointer after extend_from_slice reallocates, use-after-free (UB)
L204: name.len() as u8 truncates names over 255 bytes, corrupt frame
L218: from_utf8_unchecked on network input, UB for invalid UTF-8
L80: receive overwrites existing SKU instead of adding, resets reserved to 0
L101: release saturating_sub hides over-release
L253: Instant + ttl panics on overflow for large Duration
L259: confirm locks holds then warehouse, opposite of place_hold/sweep_expired, deadlock risk
L245: place_hold locks warehouse then holds, inverse of confirm, deadlock risk
L272: sweep_expired locks warehouse then holds, inverse of confirm, deadlock risk