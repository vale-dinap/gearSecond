The review is by reading only; I did not compile or run the code or the tests. Defects are grouped by category, most severe first.

**Undefined behaviour (`unsafe`)**

- **`lookup`, line 185:** `get_unchecked(slot)` takes `slot` from a scanner message. Any `slot >= slots.len()` is out-of-bounds UB. Use `self.slots.get(slot).copied().flatten()`, which needs no `unsafe`.
- **`append_batch`, lines 194-196:** `first` is a raw pointer into `buf`, taken before `extend_from_slice`. That call can reallocate, leaving `first` dangling, so the read at 196 is use-after-free. The pointer is also unnecessary: return `buf[start]` after the extend, or `head` directly.
- **`decode`, line 218:** `from_utf8_unchecked` runs on bytes from the network. Invalid UTF-8 there is UB. Use `std::str::from_utf8(...).map_err(|_| InvError::Malformed("bad utf-8"))?`.

**Panics**

- **`deltas`, lines 156-157:** the loop runs `i` over `0..len` and reads `prices[i + 1]`, so the last iteration indexes past the end. Any non-empty input panics; a single-element slice panics immediately. The loop should be `0..prices.len().saturating_sub(1)`, or use `windows(2)`. The subtraction at 157 can also overflow `i64` for extreme values; use `checked_sub` or `wrapping_sub` deliberately.
- **`record_loss`, line 120:** `on_hand -= lost` is not checked, so it panics in debug and wraps in release. Losing more than `on_hand` is reachable, and it is never rejected.

**Integer overflow and invariant breaks**

- **`record_loss`, line 120 (continued):** it never checks `lost <= on_hand` or `on_hand - lost >= reserved`. After a loss, `on_hand < reserved` is possible. `available()` at line 47 then underflows (`on_hand - reserved`), which panics in debug and yields a huge value in release. That value makes `reserve` accept any quantity. Reject losses that would drop `on_hand` below `reserved`.
- **`receive`, lines 79-82:** the doc says units are added to existing stock, but `insert` replaces the item and resets `reserved` to 0 (line 80). Outstanding holds then no longer match the reserved count, so stock can be oversold and a later `confirm` can ship units that belong to other holds. Fix: add to `on_hand` when the SKU exists, and keep `reserved`.
- **`total_value`, line 127:** `on_hand as u64 * price_cents` and the `sum()` can overflow `u64`. Panics in debug, wraps silently in release. Use `checked_mul` and `checked_add`, or `u128`.
- **`encode`, line 204:** `name.len() as u8` truncates names longer than 255 bytes. The length prefix then disagrees with the payload and the record is corrupted. Reject names over 255 bytes instead of truncating.

**Concurrency**

- **Lock-order inversion (`place_hold` lines 245-247 vs `confirm` lines 259-265, and `sweep_expired` 272-273):** `place_hold` and `sweep_expired` take `warehouse` then `holds`; `confirm` takes `holds` then `warehouse`. Two threads can each hold one lock and wait for the other: deadlock. Pick one order everywhere.

**Logic**

- **`confirm`, lines 260-266:** the hold is removed from the map before `ship` runs. If `ship` fails (for example, after the `receive` reset above), the hold is gone but its reservation is never released, and that stock stays reserved forever. Look up the hold, perform the ship, and only remove it on success, or release the reservation on failure.

Nothing else stood out as a real defect. `moving_average`, `SlotTable::assign`, `parse_command` and `Service::snapshot` look correct as written.

ISSUES:
L47: available() underflows when reserved > on_hand (reachable via record_loss); panic in debug, wrap in release
L80-81: receive() replaces existing item, resetting reserved to 0 while holds are outstanding; doc says units are added
L120: record_loss() does not check lost <= on_hand or on_hand >= reserved; can panic/underflow and break reserved <= on_hand
L127: total_value() u32*u64 product and u64 sum can overflow silently in release
L157: deltas() indexes prices[i + 1] with i up to len-1: out-of-bounds panic for any non-empty input; i64 subtraction can overflow
L185: lookup() uses get_unchecked on scanner-supplied slot: out-of-bounds undefined behaviour
L196: append_batch() reads through pointer taken before extend_from_slice, which can reallocate: use-after-free
L204: encode() truncates name length to u8 for names over 255 bytes: corrupt record
L218: decode() uses from_utf8_unchecked on network bytes: undefined behaviour on invalid UTF-8
L247: place_hold() locks warehouse then holds; confirm() (L259-265) locks holds then warehouse: deadlock
L266: confirm() removes hold before ship(); on ship failure the reservation is leaked permanently