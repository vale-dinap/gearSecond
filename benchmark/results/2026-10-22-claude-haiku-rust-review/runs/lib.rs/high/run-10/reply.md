I reviewed this by reading it. I haven't compiled or run it, so the UB and deadlock findings are from analysis, not reproduction.

**Memory safety (undefined behaviour)**

- **`SlotTable::lookup`, L185.** `get_unchecked` runs on a slot number from a scanner message. Any slot at or past `slots.len()` is an out-of-bounds read, which is UB. The bounds check is not a meaningful cost here. Use `self.slots.get(slot).copied().flatten()`. The return type also conflates "out of range" with "empty slot"; if callers need to distinguish them, return a `Result`.
- **`append_batch`, L194–197.** `first` is computed before `extend_from_slice`. When the extend reallocates, which is common, `first` dangles and `*first` is a use-after-free. The value is just `head`, so drop the unsafe block: `Some((head, buf.len()))`.
- **`decode`, L218.** `from_utf8_unchecked` runs on network bytes. Invalid UTF-8 produces a `String` that breaks its invariant, which is UB. Use `std::str::from_utf8(&rest[..len]).map_err(|_| InvError::Malformed("name is not UTF-8"))?`.

**Panics and overflow**

- **`Item::available`, L47.** `on_hand - reserved` panics in debug and wraps in release when `reserved > on_hand`. That state is reachable through `record_loss`. `reserve` (L91) and `low_stock` (L132) both depend on this.
- **`Warehouse::record_loss`, L120.** `on_hand -= lost` is unchecked, so losing more than is on hand underflows. It also lets `on_hand` drop below `reserved`, breaking the invariant that `available()` relies on. Reject losses larger than `on_hand` with `Insufficient`. Also decide what happens when a loss hits reserved stock, since the hold can no longer be honoured. Taking losses from unreserved stock first is the simplest rule.
- **`ship`, L112.** Same root cause: `on_hand -= qty` underflows if the invariant is already broken.
- **`total_value`, L127.** `on_hand as u64 * price_cents` and the `sum()` can both overflow `u64` with large prices or quantities. Use `checked_mul`/`checked_add`, or widen to `u128`.
- **`deltas`, L156–157.** The loop runs `i` over `0..len`, so the last iteration reads `prices[len]`. This panics on every non-empty input. The subtraction is also unchecked and can overflow for extreme `i64` values. Use `prices.windows(2).map(|w| w[1] - w[0])`. The existing tests don't cover this function, which is how the bug got through.
- **`Service::place_hold`, L253.** `Instant::now() + ttl` panics for very large caller-supplied durations such as `Duration::MAX`. Use `checked_add` and return an error.

**Logic**

- **`Warehouse::receive`, L81.** The doc comment says units are added to an existing SKU, but `insert` replaces the whole item. That resets `on_hand` to `qty` and zeroes `reserved`, discarding stock and outstanding reservations. Use `entry(sku)` with `checked_add`, and decide whether restocking should update name and price. `Service` doesn't expose `receive` today, so the damage is limited to direct `Warehouse` users. It will matter once a restock path reaches a live service.
- **`encode`, L204.** `name.len() as u8` silently truncates names longer than 255 bytes. The length prefix then disagrees with the bytes written, producing a corrupt frame. Return an error for oversize names, or reject them in `receive`.

**Concurrency**

- **Deadlock, L262.** `confirm` locks `holds` and then `warehouse`. `place_hold` (L245/L247) and `sweep_expired` (L272/L273) lock `warehouse` and then `holds`. A thread in each path can each hold one lock while waiting on the other. Pick one global lock order and apply it everywhere. Simpler still: put both maps behind a single `Mutex`, since every operation touches both.
- **Lock poisoning, throughout.** Every lock is `.unwrap()`ed. A panic inside any critical section, such as the underflows above, poisons that mutex, and every later call panics. Fix the panics, and handle `PoisonError` deliberately if you want the service to survive them.
- **Minor, `confirm` L264–266.** The hold is removed before `ship` runs. If `ship` ever fails, the hold is gone but its reservation remains. The invariant holds today, so this is latent. Check first, then mutate.

**Not defects, but worth a look**

- `Warehouse::log` grows without bound in a long-running service. Consider a bounded buffer or an external sink.
- `release` clamps silently with `saturating_sub`, which can hide accounting bugs. Returning an error when `qty > reserved` would surface them.
- `decode` ignores trailing bytes, so concatenated records can't be framed reliably. Return the consumed length, or reject trailing input.
- `sweep_expired` discards the `release` result with `let _`.

`parse_command`, `moving_average`, and the guard in `reserve` are correct as written.

To verify: Miri on `append_batch`, `lookup`, and `decode` should flag the UB. Add a `deltas` test with `&[1, 2]`. A stress test or loom model of `confirm` against `place_hold` would confirm the deadlock.

ISSUES:
L47: available() underflows when reserved > on_hand (reachable via record_loss)
L81: receive replaces an existing SKU instead of adding stock; resets on_hand and reserved
L120: record_loss underflows on_hand and can push on_hand below reserved
L127: total_value overflows u64 in the multiply and sum
L157: deltas indexes prices[len] and panics on any non-empty input; i64 subtraction can overflow
L185: get_unchecked on a scanner-supplied slot is an out-of-bounds read (UB)
L196: dereferences a pointer invalidated by extend_from_slice reallocation (use-after-free)
L204: name.len() as u8 truncates names over 255 bytes and corrupts the frame
L218: from_utf8_unchecked on untrusted network bytes (UB on invalid UTF-8)
L253: Instant + caller-supplied ttl panics on overflow
L262: confirm's lock order is inverted relative to place_hold and sweep_expired (deadlock)