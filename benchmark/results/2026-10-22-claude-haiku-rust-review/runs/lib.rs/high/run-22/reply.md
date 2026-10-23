I reviewed the module by reading it. I did not compile it or run the tests, and the existing tests don't exercise any of the defects below. The most serious problems are a deadlock, two sources of undefined behaviour, and an out-of-bounds panic in `deltas` that fires on every non-empty input.

**Critical**

1. **Deadlock between `place_hold` and `confirm` (L247, L259–265).** `place_hold` locks `warehouse` and then `holds`. `confirm` locks `holds` and then `warehouse`. If one thread is in each function, both wait forever. `sweep_expired` (L272–273) uses the same order as `place_hold`, so it has the same risk. Fix by taking locks in one global order everywhere, or by putting `warehouse` and `holds` behind a single `Mutex`.

2. **`deltas` panics on every non-empty input (L156–157).** The loop runs `i` over `0..prices.len()`, so on the last iteration `prices[i + 1]` indexes past the end. The fix is `prices.windows(2).map(|w| w[1] - w[0]).collect()`. That also makes the expected length explicit. The `i64` subtraction can still overflow for extreme inputs, so use `checked_sub` or `wrapping_sub` if that matters.

3. **Out-of-bounds read in `lookup` (L185).** `get_unchecked` takes a `slot` that the doc comment says comes straight from a scanner message. Any out-of-range value is undefined behaviour. The bounds check is cheap, so use `self.slots.get(slot).copied().flatten()`.

4. **Use of a possibly dangling pointer in `append_batch` (L194–196).** `first` is computed after `push` but before `extend_from_slice`. The `extend` can reallocate the buffer, and then `*first` reads freed memory. The raw pointer isn't needed. The first value is just `head`, so return `(head, buf.len())`.

5. **Unchecked UTF-8 on network input in `decode` (L218).** `from_utf8_unchecked` on attacker-controlled bytes is undefined behaviour when they are not valid UTF-8. Use `std::str::from_utf8(...).map_err(|_| InvError::Malformed("bad utf-8"))?`.

**High**

6. **`encode` silently corrupts names longer than 255 bytes (L204).** `name.len() as u8` wraps, so the length prefix no longer matches the payload and every following field is misread. Reject names longer than 255 bytes with an error, or truncate them deliberately.

7. **`receive` overwrites existing stock (L80–81).** `HashMap::insert` replaces the whole `Item`, which resets `reserved` to 0 and replaces the name and price. The doc comment says units should be added to the existing SKU. Outstanding holds then point at reservations that no longer exist, so later `ship` calls fail or stock is oversold. Use `entry(sku).or_insert(...)` and add `qty` to `on_hand`.

8. **`record_loss` can underflow and ignores reservations (L120).** If `lost > on_hand`, the subtraction panics in debug and wraps in release, which turns a loss into about 4 billion units. Losses can also push `on_hand` below `reserved`, and that breaks the invariant in item 9.

9. **`available()` underflows (L47).** It assumes `reserved <= on_hand`, but `record_loss` and `receive` can break that. Debug builds panic in `reserve` and `low_stock`. Release builds wrap to a huge value, so `reserve` will allow overselling. Either enforce the invariant in `record_loss`, or use `saturating_sub` here and report the discrepancy.

10. **A failed `ship` in `confirm` discards the hold (L266).** The hold is removed from the map at L260 before `ship` runs. If `ship` returns `Insufficient`, the hold is gone but its units stay reserved forever, and nothing can release them. Remove the hold only after `ship` succeeds, or put it back on error.

11. **`place_hold` can panic after reserving stock (L253).** `Instant::now() + ttl` panics on overflow, for example with `Duration::MAX`. That happens after `wh.reserve` has succeeded and while the locks are held. The result is a leaked reservation plus poisoned mutexes, and every later `lock().unwrap()` then panics. Compute the expiry with `checked_add` before reserving, and return an error if it overflows.

**Medium / low**

12. **`total_value` can overflow (L127).** `on_hand as u64 * price_cents` and the `.sum()` are unchecked. Large prices or quantities wrap in release and panic in debug. Use `checked_mul` and `checked_add`, or return an error.

13. **`release` hides double-releases (L101).** `saturating_sub` turns an over-release into a silent no-op, so accounting bugs are hidden. Consider returning an error when `qty > reserved`.

Other observations, not counted as defects:
- Every `lock().unwrap()` turns one panic into a permanent outage, because the mutex stays poisoned. Consider recovering with `unwrap_or_else(|e| e.into_inner())` if the state is still valid after a panic.
- `moving_average` panics on `window == 0` (L144). That's a documented precondition, so it's acceptable if callers can't pass zero.
- `log` grows without limit.
- `sweep_expired` is never called automatically, so expired holds keep stock reserved until something calls it.
- `decode` accepts trailing bytes without complaint, which may be fine if records are framed elsewhere.

ISSUES:
L247: place_hold takes holds while holding warehouse, but confirm and sweep_expired take the locks in the opposite order, so the two can deadlock
L157: deltas indexes prices[i + 1] on the last iteration and panics on every non-empty input
L185: lookup uses get_unchecked on a scanner-supplied index, which is an out-of-bounds read (undefined behaviour)
L196: append_batch dereferences a pointer that extend_from_slice can invalidate by reallocating (undefined behaviour)
L218: decode uses from_utf8_unchecked on network bytes, which is undefined behaviour for invalid UTF-8
L204: encode truncates names longer than 255 bytes to a u8 length prefix, corrupting the record
L81: receive replaces an existing item instead of adding to it, resetting reserved, name and price
L266: confirm removes the hold before ship, so a failed ship leaks the reserved units
L253: place_hold can panic on Instant + ttl after reserving stock, poisoning the mutexes and leaking the reservation
L120: record_loss subtracts without checking lost <= on_hand, and ignores reservations
L47: available() underflows when reserved exceeds on_hand, which record_loss can cause
L127: total_value multiplies and sums in u64 without overflow checks
L101: release uses saturating_sub, which silently hides over-release bugs