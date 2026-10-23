I reviewed the file by reading it. I did not compile it, run the tests, or run Miri, so the findings below are from static analysis. Ordered by severity:

**Undefined behaviour and memory safety**

- **`append_batch`, L193-197: use-after-free.** `first` is a raw pointer to the head element, taken before `extend_from_slice(tail)`. When the extend has to grow the buffer, the old allocation is freed and `*first` reads freed memory. Small test inputs won't trigger the reallocation, so the bug can pass tests. The unsafe block is also unnecessary, since the value read is just `head`. Fix: `Some((head, buf.len()))`.
- **`SlotTable::lookup`, L185: out-of-bounds read.** `slot` comes from a scanner message, so it is untrusted. `get_unchecked` with an index at or beyond `len` is UB. A bounds check is cheap, so the "hot path" comment doesn't justify removing it. Fix: `self.slots.get(slot).copied().flatten()`.
- **`decode`, L218: invalid UTF-8 is UB.** `from_utf8_unchecked` runs on bytes from the network, and a peer can send bytes that aren't valid UTF-8. Fix: `std::str::from_utf8(&rest[..len]).map_err(|_| InvError::Malformed("name not UTF-8"))?.to_string()`.

**Panics**

- **`deltas`, L156-157: panics on every non-empty input.** `i` runs over `0..prices.len()`, so on the last iteration `prices[i + 1]` is out of bounds. `deltas(&[5])` panics. The subtraction can also overflow `i64` (e.g. `[i64::MAX, -1]`). Fix: `prices.windows(2).map(|w| w[1] - w[0]).collect()`, and use `checked_sub` if overflow should be an error.
- **`record_loss`, L120, and `available`, L47: underflow.** `on_hand -= lost` is unchecked. If `lost > on_hand`, it panics in debug and wraps to about 4.29 billion in release, which creates phantom stock. It also ignores reservations. Losing reserved units leaves `on_hand < reserved`, and then `available()` at L47 underflows. `reserve`, `low_stock`, and `ship` (L112) all depend on that value. Fix: reject losses beyond `on_hand - reserved` (or reduce `reserved` too), and use checked arithmetic.
- **`place_hold`, L253: panic on large TTL.** `Instant::now() + ttl` panics when the result isn't representable, for example with `Duration::MAX`. Use `checked_add` and return an error.
- **Poison cascade.** Every lock is `.unwrap()`ed. Any panic while a guard is held (such as the overflows above) poisons the mutex, and every later call panics too.

**Logic errors**

- **`receive`, L79-82: contradicts its doc and corrupts stock.** The doc says units are added to an existing SKU, but the code inserts a new `Item`. Receiving 10 units into a SKU with 10 on hand leaves 10 on hand, so 10 units vanish from the records. It also resets `reserved` to 0 while holds may still be outstanding. For example: `receive(1,"bolt",10,25)`, `reserve(1,10)`, `receive(1,"bolt",10,25)`, `reserve(1,10)`. The second reserve succeeds, leaving 10 on hand against two holds of 10. Confirming the first hold ships the stock. Confirming the second hits the `Insufficient` error at L109, but `confirm` has already removed the hold at L260, so that customer's hold is lost. Fix: use `entry(sku)` and add `qty` to `on_hand`, keeping `reserved` and the other fields intact.
- **`encode`, L204: silent truncation corrupts frames.** `name.len() as u8` wraps for names longer than 255 bytes, but every name byte is still written. A 300-byte name writes length byte 44 followed by 300 bytes, and every later field is misread. `receive` accepts names of any length, so this is reachable. Fix: return `Result` and reject names over 255 bytes, or enforce the limit in `receive`. The round-trip test misses this because it uses a 3-byte name.
- **`total_value`, L127: overflow.** `on_hand as u64 * price_cents` and the `sum` can overflow `u64`. Panic in debug, wrap in release. This needs large prices, but `price_cents` is unbounded. Use `checked_mul`/`checked_add`, or `u128` if the total is reported as-is.

**Concurrency**

- **Lock-order inversion (deadlock), L259 against L245-247 and L272-273.** `confirm` takes `holds` and then `warehouse`. `place_hold` and `sweep_expired` take `warehouse` and then `holds`. If one thread is in `confirm` holding `holds` while another is in `place_hold` holding `warehouse`, both block forever. This can happen under ordinary concurrent use. Fix: take `warehouse` first in `confirm` so every path uses the same order.

**Smaller notes**

- `log` (L69) grows without bound in a long-running service. Worth capping.
- `decode` ignores trailing bytes and doesn't return the number of bytes consumed, so it can't parse a stream of records.
- The tests don't exercise any of the paths above. Add cases for `deltas(&[5])`, names over 255 bytes, non-UTF-8 input, `record_loss` beyond `on_hand`, and concurrent `confirm`/`place_hold`.

ISSUES:
L47: available() underflows once reserved exceeds on_hand (reachable through record_loss)
L81: receive overwrites an existing SKU instead of adding stock, resetting reserved and losing units
L120: record_loss subtracts unchecked and ignores reservations, causing underflow or wrap
L127: total_value multiplies and sums in u64 without overflow checks
L156: deltas indexes prices[len] and panics on any non-empty input; subtraction can overflow i64
L185: lookup uses get_unchecked on an untrusted slot index (out-of-bounds UB)
L196: append_batch dereferences a pointer invalidated by extend_from_slice reallocation (use-after-free)
L204: encode truncates name length to u8 without a check, corrupting the frame
L218: decode uses from_utf8_unchecked on untrusted bytes (UB on invalid UTF-8)
L253: place_hold panics on Instant + Duration overflow for large ttl
L259: confirm locks holds before warehouse, opposite to place_hold and sweep_expired (deadlock)