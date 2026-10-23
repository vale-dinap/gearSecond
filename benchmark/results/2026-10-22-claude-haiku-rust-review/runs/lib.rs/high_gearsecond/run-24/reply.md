I reviewed the module by reading it. I did not compile or run it, so the findings below are from static analysis.

## Panics and undefined behaviour

- **`deltas` always panics on non-empty input (L157).** The loop runs `i` over `0..prices.len()`, so on the last iteration `prices[i + 1]` indexes one past the end. The subtraction can also overflow `i64`. Iterate `prices.windows(2)` and use `checked_sub` or `wrapping_sub` as the intent requires.
- **`SlotTable::lookup` is undefined behaviour on bad input (L185).** `get_unchecked` is called with a slot that the comment says comes from a scanner message, which is untrusted. Any out-of-range slot is UB. The bounds check is cheap, so use `self.slots.get(slot).copied().flatten()` and drop the `unsafe`.
- **`append_batch` reads a dangling pointer (L194–196).** `first` is computed from `buf.as_ptr()` before `extend_from_slice`. When the extend reallocates the vector, `first` points into freed memory, and `*first` is use-after-free. Read `buf[start]` after the extend, or return `head` directly. The `unsafe` block isn't needed.
- **`decode` builds a `String` from unchecked bytes (L218).** The input comes from the network, so invalid UTF-8 is a soundness violation. Use `String::from_utf8(...)` and map the error to `InvError::Malformed`.

## Integer overflow and underflow

- **`record_loss` can underflow `on_hand` (L120).** Nothing checks `lost <= on_hand`. This panics in debug builds and wraps to a huge value in release.
- **`record_loss` breaks the `reserved <= on_hand` invariant.** It doesn't clamp or reject reserved units, so `available()` (L47) can underflow later. A `reserved > on_hand` state is reachable through this path. Reject losses that would drop `on_hand` below `reserved`, or clamp `reserved`.
- **`ship` can underflow `on_hand` (L112).** It checks `qty <= reserved` but not `qty <= on_hand`. This follows from the invariant break above.
- **`place_hold` can panic on a large TTL (L253).** `Instant::now() + ttl` panics on overflow. Use `checked_add` and return an error.
- **`total_value` can overflow (L127).** `on_hand as u64 * price_cents` and the `sum()` are unchecked. Use `checked_mul` and `checked_add` or `saturating_*`, depending on the desired behaviour.

## Logic errors

- **`receive` overwrites existing stock (L79–81).** The doc comment says units are added to what is on hand. The code inserts a fresh `Item`, which resets `reserved` to 0 and replaces the name and price. Outstanding holds then no longer match the reserved count, which allows overselling. Use `entry(sku)` and add `qty` to `on_hand`, keeping the existing name and price unless the caller means to change them.
- **`encode` truncates long names (L204).** `name.len() as u8` wraps for names over 255 bytes. The length byte then disagrees with the payload, and the encoded record is corrupt. Reject names longer than 255 bytes, or return an error from `encode`.
- **`encode` writes `on_hand` where the format comment says `qty` (L207).** This may be intended, but the wire doc and the field name differ. Confirm which the receiver expects.
- **`confirm` loses the hold if `ship` fails (L260, L266).** The hold is removed from the map before the ship. If `ship` returns `Insufficient`, for example after a loss, the hold is gone while its reservation still counts against stock, so those units are leaked. Restore the hold on error, or ship first and remove the hold only on success.
- **`log` grows without bound (L69, L82).** Every receive, ship and loss appends a `String`, and nothing trims it. In a long-running service this is a memory leak. Use a bounded buffer or move the log out to the caller.

## Concurrency

- **Lock-order inversion can deadlock (L259 vs L245/247 and L272–273).** `confirm` takes `holds` and then `warehouse`. `place_hold` and `sweep_expired` take `warehouse` and then `holds`. If one thread is in `confirm` holding `holds` while another is in `place_hold` holding `warehouse`, both block forever. Pick one order everywhere, or fold `holds` and `warehouse` under a single lock.
- **`next_id` has its own mutex (L236, L249).** It is taken while `warehouse` and `holds` are held, which adds another lock to the ordering problem. A plain `AtomicU64` with `fetch_add` removes it.

## Not defects, but worth checking

- `moving_average` asserts when `window == 0` (L144). That's acceptable for a library function, but make sure no caller passes untrusted input there.
- `parse_command` requires uppercase verbs. That is a behaviour choice, not a bug.

ISSUES:
L47: available() underflows when reserved exceeds on_hand, which record_loss can cause
L79: receive overwrites existing item, resetting reserved and breaking hold accounting
L112: ship subtracts qty from on_hand without checking it, can underflow
L120: record_loss underflows on_hand without bounds check
L127: total_value multiplies and sums u64 unchecked, can overflow
L157: deltas indexes prices[i+1] past end, panics on any non-empty input
L185: lookup uses get_unchecked on untrusted slot index, undefined behaviour
L196: append_batch reads pointer computed before reallocation, use-after-free
L204: encode casts name length to u8 without check, truncates names over 255 bytes
L218: decode uses from_utf8_unchecked on untrusted network bytes, undefined behaviour
L253: place_hold Instant + ttl panics on overflow
L259: confirm takes holds then warehouse, opposite order to place_hold, deadlock risk
L266: confirm removes hold before ship, leaks reservation when ship fails
L69: log Vec grows unbounded, memory leak in long-running service