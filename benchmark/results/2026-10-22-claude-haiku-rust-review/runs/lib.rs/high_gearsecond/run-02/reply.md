## Findings

**Memory safety and undefined behaviour (most serious)**

- **`SlotTable::lookup`, L185:** `get_unchecked` runs on `slot`, which the comment says comes from a scanner message. Any slot ≥ `slots.len()` is an out-of-bounds read, which is UB. The "hot path" justification doesn't hold for untrusted input. Use `self.slots.get(slot).copied().flatten()`.
- **`append_batch`, L193–196:** `first` is a raw pointer into `buf` taken before `extend_from_slice`. When the extend reallocates (common when capacity runs out), `first` dangles and `*first` is a use-after-free. The pointer adds nothing: `head` is already the first SKU, so return `Some((head, buf.len()))`.
- **`decode`, L218:** `from_utf8_unchecked` runs on bytes from the network. Invalid UTF-8 produces a `String` that violates its invariant, which is UB. Use `std::str::from_utf8(...).map_err(|_| InvError::Malformed("bad utf-8"))?`.

**Concurrency**

- **`Service`, L245–247 vs L259–265:** `place_hold` takes `warehouse` then `holds`. `confirm` takes `holds` then `warehouse`. `sweep_expired` takes `warehouse` then `holds`. Two threads can each hold one lock and wait for the other, which deadlocks. Pick one global order (or guard both with a single mutex) and apply it everywhere.
- **`confirm`, L259–266:** the hold is removed from the map before `ship` runs. If `ship` fails (for example `Insufficient`, which can happen after the `receive` reset above), the hold is gone and its reserved units are never released. The hold should be removed only after success, or restored on error.

**Integer overflow and underflow**

- **`Item::available`, L47:** `on_hand - reserved` underflows whenever `reserved > on_hand`. That panics in debug and wraps in release. A wrapped value is huge, so `reserve` (L91–92) would accept over-reservations. This invariant can be broken by `record_loss` (below).
- **`record_loss`, L120:** `on_hand -= lost` is unchecked and does not reduce `reserved` or check `lost <= on_hand`. The `ship` arithmetic at L111–112 is safe only while `reserved <= on_hand` holds, and this breaks it.
- **`total_value`, L127:** `on_hand as u64 * price_cents` and the `sum()` can overflow `u64`. Use `checked_mul` / `checked_add` or `saturating_*` and decide what overflow should mean.
- **`deltas`, L157:** `prices[i + 1] - prices[i]` overflows for values near `i64::MIN` and `i64::MAX`. Use `checked_sub` and return an error, or use `windows(2)` with `checked_sub`.

**Logic errors**

- **`deltas`, L156:** the loop runs `0..prices.len()`, so at `i = len - 1` it reads `prices[len]` and panics. This happens for every non-empty input. Use `0..prices.len().saturating_sub(1)` or `prices.windows(2)`. The `with_capacity` at L155 already assumes this.
- **`receive`, L79–81:** the doc says units are added to an existing SKU, but the code replaces the whole item. It sets `on_hand = qty`, drops the existing stock count, and resets `reserved` to 0 while holds may still be outstanding. Add to `on_hand` for existing SKUs and keep the reservation.
- **`encode`, L204:** `name.len() as u8` silently truncates names over 255 bytes, and the full name is still written. The record then decodes as garbage. Return an error for names that are too long.

**Not defects, but worth knowing**

- `moving_average` (L144) panics on `window == 0`. That is a documented assert, so it is a design choice and not a bug.
- `.lock().unwrap()` (throughout `Service`) panics if a mutex is poisoned. Acceptable for this scope.
- I did not compile or run the tests. These findings come from reading the code.

ISSUES:
L47: available() underflows when reserved > on_hand; panics in debug, wraps in release and allows over-reservation
L79: receive() replaces existing SKU: resets on_hand and reserved, discarding stock and outstanding reservations
L120: record_loss() subtracts unchecked and can leave on_hand < reserved, breaking the invariant
L127: total_value() u64 multiplication and sum can overflow
L156: deltas() loop reads prices[len] and panics on every non-empty input
L157: deltas() i64 subtraction can overflow
L185: lookup() uses get_unchecked on an untrusted scanner slot: out-of-bounds read (UB)
L196: append_batch() reads through pointer that dangles after extend reallocates buf (UB)
L204: encode() truncates names longer than 255 bytes with `as u8`, corrupting the record
L218: decode() uses from_utf8_unchecked on network bytes: invalid UTF-8 is UB
L259: confirm() takes holds then warehouse, opposite to place_hold() (L245): lock-order deadlock
L266: confirm() removes the hold before ship(); on failure the hold and its reservation are lost