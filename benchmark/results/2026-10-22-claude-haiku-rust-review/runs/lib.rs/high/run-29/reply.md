I found several defects that should block the merge: two undefined-behaviour sites reachable from untrusted input, a `deltas` function that panics on every non-empty input, and a lock-order inversion that can deadlock. Line numbers refer to the listing.

**Undefined behaviour**

- **`SlotTable::lookup` (L185)** calls `get_unchecked` on a slot index that comes from a scanner message, with no bounds check. An out-of-range slot reads past the end of the allocation. `self.slots.get(slot).copied().flatten()` is safe and costs almost nothing, so the `unsafe` block isn't worth keeping.
- **`append_batch` (L194–196)** takes `first` as a raw pointer into `buf` before `extend_from_slice` (L195). That call can reallocate, which leaves `first` dangling, and L196 reads through it. The return value is just the batch's first SKU, which is already `head`, so the pointer code can go and the function can return `head`.
- **`decode` (L218)** runs `from_utf8_unchecked` on bytes from the network. Invalid UTF-8 produces an invalid `String`, which is UB. Use `std::str::from_utf8` and map the error to `Malformed`.

**Panics and overflow**

- **`deltas` (L156–157)** loops over `0..prices.len()` and reads `prices[i + 1]`. On the last iteration that index is `len`, so every non-empty input panics; `deltas(&[5])` panics immediately. `prices.windows(2).map(|w| w[1] - w[0])` fixes this. The subtraction at L157 can also overflow `i64` for extreme prices.
- **`available` (L47)** computes `on_hand - reserved`, which underflows once `reserved > on_hand`. `record_loss` can produce that state (see L120). In debug builds this panics. In release builds it wraps to about 4 billion, and `reserve` then accepts oversold units.
- **`record_loss` (L120)** does no bounds check, so `lost > on_hand` underflows. It also never checks that the remaining stock still covers existing reservations.
- **`ship` (L112)** subtracts from `on_hand` after checking only `reserved`. Once `record_loss` has broken the invariant, this can underflow too.
- **`total_value` (L127)** multiplies `on_hand as u64 * price_cents` and then sums the results in `u64`. Both can overflow with large quantities and prices. `u128` or checked arithmetic would prevent it.
- **`place_hold` (L253)** does `Instant::now() + ttl`. `Duration` is caller input, and `Instant` addition panics on overflow. Use `checked_add` and return an error.
- **`encode` (L204)** does `name.len() as u8`, which silently truncates names of 256 bytes or more. A 256-byte name gets length prefix 0 followed by 256 bytes, so the record is corrupt. It should be rejected.

**Concurrency**

- **Deadlock (L265, against L245/L247 and L272/L273).** `place_hold` and `sweep_expired` lock `warehouse` and then `holds`. `confirm` locks `holds` (L259) and then `warehouse` (L262/L265). If `confirm` holds `holds` while `place_hold` holds `warehouse`, each waits on the other. Pick one lock order everywhere, or put the warehouse and holds behind a single mutex.
- **Poisoning.** Every lock uses `.unwrap()`. Any panic from the arithmetic above while a guard is held poisons the mutex, and every later call then panics too. That amplifies the panic bugs into a full service outage.

**Logic**

- **`receive` (L81)** uses `insert`, which replaces the existing record. The doc comment (L77–78) says units should be added to existing stock, but the code resets `on_hand` to `qty` and `reserved` to 0. That drops stock and live reservations, so later `ship` and `release` calls work against wrong counts.
- **`release` (L101)** uses `saturating_sub`, which hides over-releases. This is how the mismatch above would go unnoticed. Returning an error when `qty > reserved` would surface it.
- **`confirm` (L266)** removes the hold at L260 before `ship` runs. If `ship` fails, the hold is gone and its units stay reserved permanently.

**Checked and fine:** `moving_average` (an empty window range is handled, and `end - window` can't underflow), `parse_command`, and the length checks in `decode`. The existing tests don't exercise any of the defects above. I'd add tests for `deltas` on a single element, `record_loss` followed by `reserve`, and concurrent `confirm` with `place_hold`.

ISSUES:
L47: available() underflows when reserved > on_hand; panics in debug, wraps in release and allows overselling
L81: receive() replaces an existing item, discarding on_hand and live reservations
L101: release() saturates silently, hiding over-release
L112: ship() subtracts from on_hand without checking it covers the units
L120: record_loss() has no bounds check; underflows and can leave reserved > on_hand
L127: total_value() multiplication and sum can overflow u64
L156: deltas() indexes prices[len]; panics on every non-empty input
L157: deltas() i64 subtraction can overflow
L185: get_unchecked on an untrusted slot index is an out-of-bounds read (UB)
L196: reads through a pointer that extend_from_slice may have invalidated (UB)
L204: name length truncated to u8, producing corrupt wire records
L218: from_utf8_unchecked on untrusted bytes can create an invalid String (UB)
L253: Instant + Duration panics for a large caller-supplied ttl
L265: lock-order inversion with place_hold and sweep_expired can deadlock
L266: hold is removed before ship(); if ship fails, reserved units leak permanently