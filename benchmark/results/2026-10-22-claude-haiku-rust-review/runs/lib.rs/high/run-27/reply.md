I reviewed this by reading it; I did not compile or run it. The findings are grouped by severity. The existing tests cover none of them.

**Undefined behaviour**

1. **`SlotTable::lookup` (L185):** `get_unchecked` is called with a slot index that the comment says comes from a scanner message. Any slot at or beyond `slots.len()` is an out-of-bounds read, reachable from outside the process. The bounds check is a single comparison, so the "hot path" justification doesn't hold. Use `self.slots.get(slot).copied().flatten()`.

2. **`decode` (L218):** `from_utf8_unchecked` runs on bytes from the network. Invalid UTF-8 produces a `String` that violates its invariant, which is UB. Use `std::str::from_utf8(...)` and map the error to `InvError::Malformed`.

3. **`append_batch` (L194–196):** `first` is a raw pointer into `buf`, taken before `extend_from_slice(tail)`. If the tail forces a reallocation, `first` dangles and L196 reads freed memory. This only happens when capacity is exceeded, so small test inputs won't reveal it. The pointer isn't needed anyway: the first SKU is `head`, so return `head`.

**Panics and arithmetic**

4. **`deltas` (L156–157):** The loop runs `i` over `0..prices.len()`, so on the last iteration `prices[i + 1]` indexes `prices.len()`. Every non-empty input panics; `deltas(&[1])` panics. `prices.windows(2)` fixes this. Subtracting two `i64`s can still overflow for extreme values, so use `checked_sub` or `saturating_sub`.

5. **`record_loss` (L120):** Nothing checks `lost <= on_hand`. In debug it panics; in release it wraps to about 4 billion phantom units. It also ignores `reserved`, so a loss can push `on_hand` below `reserved`.

6. **`Item::available` (L47):** `on_hand - reserved` assumes `reserved <= on_hand`, which nothing enforces. `record_loss` breaks it, and so does `receive` (see 10). Example: on_hand 10, reserved 8, then `record_loss(5)` leaves on_hand 5 and reserved 8. `available()` then panics in debug, or wraps to a huge value in release, and `reserve` would accept orders the shelf can't fill.

7. **`total_value` (L127):** `on_hand as u64 * price_cents` and the `sum()` can overflow `u64` with large prices or quantities. Use checked arithmetic or `u128`.

8. **`place_hold` (L253):** `Instant::now() + ttl` panics for a large `Duration`, and the caller controls `ttl`. Use `checked_add` and return an error.

9. **`encode` (L204):** `name.len() as u8` silently truncates names over 255 bytes, but all name bytes are still written. The decoder then reads the wrong length and misparses the frame. Reject long names with an error, or enforce the limit in `receive`.

**Logic**

10. **`receive` (L79–81):** The doc says units are added to existing stock, but `insert` replaces the whole record. On-hand is set to `qty`, `reserved` is reset to 0 while `Hold`s still reference it, and name and price are overwritten. Restocking an SKU with outstanding holds makes the counter and the holds diverge. Later saturating releases then reduce reservations belonging to other holds. Fix: `item.on_hand = item.on_hand.checked_add(qty)` on the existing record, and update name or price only if that is intended.

11. **`Service::confirm` (L260–266):** The hold is removed before `ship` runs. If `ship` fails, which 6 and 10 make possible, the hold is gone but its units stay counted as reserved forever. The stock is stranded and the caller can't retry. Remove the hold only after `ship` succeeds.

12. **`release` (L101):** `saturating_sub` absorbs over-release silently, which hides the bookkeeping errors above. Returning an error when `qty > reserved` would surface them.

**Concurrency**

13. **Lock-order inversion (L245–247 vs. L262/L265):** `place_hold` and `sweep_expired` take `warehouse` then `holds`. `confirm` takes `holds` then `warehouse`. If `confirm` holds `holds` while `place_hold` holds `warehouse`, each waits on the other, so this can deadlock under normal load. Use one lock order everywhere, or put both pieces of state behind a single mutex.

**Low**

14. **`log` (L69):** The audit log grows without bound in a long-running service.

15. **`moving_average` (L144):** The `assert!` panics on `window == 0` in a public function. Return a `Result` or document a `# Panics` section.

Tests worth adding before merge: `deltas(&[1])`, `append_batch` into a `Vec` at exact capacity, `lookup` past the end, `decode` of invalid UTF-8, `record_loss` beyond `on_hand`, `encode` of a 256-byte name, and a two-thread test of `confirm` against `place_hold`.

ISSUES:
L47: available() underflows when reserved exceeds on_hand
L69: audit log grows without bound
L79: receive() overwrites the record, resetting reserved and contradicting its doc
L101: release() saturating_sub silently absorbs over-release
L120: record_loss() does not bound loss by on_hand; underflow wraps in release
L127: total_value() can overflow u64
L144: moving_average() panics on window 0 in a public API
L156: deltas() indexes prices[len] on the last iteration; panics on any non-empty input
L157: deltas() i64 subtraction can overflow
L185: lookup() uses get_unchecked on an untrusted slot index (out-of-bounds UB)
L194: append_batch() keeps a raw pointer across extend_from_slice; dangling read on reallocation (UB)
L204: encode() truncates name length to u8, corrupting the frame
L218: decode() uses from_utf8_unchecked on untrusted bytes (UB on invalid UTF-8)
L245: place_hold() locks warehouse then holds, opposite to confirm(); deadlock risk
L253: place_hold() Instant + ttl panics on large Duration
L260: confirm() removes the hold before ship(); reservation leaks on failure
L262: confirm() takes warehouse lock while holding holds; lock-order inversion