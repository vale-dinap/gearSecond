## Findings

I found 12 real defects. The worst are the `unsafe` blocks on untrusted input, a panic in `deltas` that hits every non-empty input, and a lock-order inversion that can deadlock. I did not compile or run the code; these come from reading it.

### Memory safety and undefined behaviour

- **L218, `decode`:** `from_utf8_unchecked` runs on bytes from the network. Invalid UTF-8 makes the `String` invalid, which is undefined behaviour. Use `std::str::from_utf8(...)` and map the error to `Malformed`.
- **L185, `SlotTable::lookup`:** `get_unchecked` runs on `slot`, which the comment says comes from a scanner message. Any `slot >= len` is an out-of-bounds read. Use `self.slots.get(slot).copied().flatten()`. The "hot path" saving is not worth it here.
- **L194–197, `append_batch`:** `first` is a raw pointer into `buf` taken before `extend_from_slice`. That call can reallocate, so the dereference at L196 reads freed memory. Use `buf.extend_from_slice(batch); Some((batch[0], buf.len()))`, which needs no pointer at all.

### Panics

- **L157, `deltas`:** the loop runs `i` over `0..prices.len()` and indexes `prices[i + 1]`. On the last iteration that is `prices[len]`, which is out of bounds. Every non-empty input panics. Use `prices.windows(2).map(|w| w[1] - w[0]).collect()`.
- **L157:** the `i64` subtraction can overflow for extreme prices. Use `checked_sub` or `saturating_sub`.
- **L253, `place_hold`:** `Instant::now() + ttl` panics when `ttl` is very large, for example `Duration::MAX`. Use `checked_add` and return an error.
- **L47, `Item::available`:** `on_hand - reserved` underflows whenever `reserved > on_hand`. That state is reachable through `record_loss` (see below). Use `saturating_sub`, or keep the invariant enforced everywhere.
- **L111–112 and L120:** `ship` and `record_loss` subtract without checking. `record_loss` can take `on_hand` below `reserved`, after which `available()` underflows, and in release builds the subtraction wraps silently.

### Logic

- **L79–81, `receive`:** the doc says units are added to an existing SKU, but `insert` replaces the whole item. Existing stock is lost, and `reserved` resets to 0 while holds are still outstanding. The name and price are also overwritten. Use `entry(sku)` and add to `on_hand`.
- **L120, `record_loss`:** there is no check that `lost` is within stock, and it does not reduce reservations. Decide whether losses can consume reserved units, then check and adjust both fields.
- **L204, `encode`:** `name.len() as u8` silently truncates names longer than 255 bytes. The frame then has a wrong length prefix and decodes as garbage. Return an error for names over 255 bytes, which means `encode` should return `Result`.

### Concurrency

- **L259–265 (`confirm`) vs. L245–247 (`place_hold`) and L272–273 (`sweep_expired`):** `confirm` locks `holds` and then `warehouse`. `place_hold` and `sweep_expired` lock `warehouse` and then `holds`. Two threads can each hold one lock and wait for the other, which is a deadlock. Pick one lock order everywhere, or put both pieces of state behind one `Mutex`.

### Overflow

- **L127, `total_value`:** `on_hand as u64 * price_cents` and the `sum` can overflow `u64` with large prices. Use `checked_mul` and `checked_add`, or saturate.

### Not defects, but worth knowing

- `confirm` removes the hold before a failing `ship` (L266), so a failure there would leak the reservation. Through `Service` this looks unreachable, because the `Warehouse` is private and only the hold-removing paths call `release` and `ship`. A later change could make it reachable.
- The tests cover only the happy paths. None touch `deltas`, `receive` on an existing SKU, `append_batch`, the concurrency paths, or any malformed input to `decode`.

ISSUES:
L47: available() underflows when reserved > on_hand (reachable via record_loss)
L79: receive() replaces existing item instead of adding; loses stock and reserved count
L120: record_loss() unchecked subtraction; on_hand can underflow or drop below reserved
L127: total_value() u64 multiply and sum can overflow
L157: deltas() indexes prices[len] on last iteration; panics on any non-empty input
L157: deltas() i64 subtraction can overflow
L185: lookup() get_unchecked on untrusted slot index; out-of-bounds read (UB)
L196: append_batch() dereferences pointer invalidated by extend_from_slice reallocation (UB)
L204: encode() name.len() as u8 truncates names over 255 bytes; corrupt frames
L218: decode() from_utf8_unchecked on untrusted bytes; invalid UTF-8 is UB
L253: place_hold() Instant + ttl panics on overflow for very large ttl
L259: confirm() locks holds then warehouse; place_hold/sweep lock warehouse then holds; deadlock