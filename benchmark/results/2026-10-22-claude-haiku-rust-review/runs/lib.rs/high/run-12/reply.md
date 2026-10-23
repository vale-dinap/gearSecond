The most serious problems are two undefined-behaviour sites reachable from untrusted input (`lookup`, `decode`), a use-after-free in `append_batch`, a `deltas` that panics on every non-empty input, and a lock-order deadlock between `place_hold` and `confirm`. The inventory arithmetic also breaks down once `record_loss` runs. Line numbers refer to the listing.

## Undefined behaviour and memory safety

**`SlotTable::lookup`, L185.** `get_unchecked` is called with `slot`, which the doc comment says comes from a scanner message. Any slot at or past `slots.len()` is an out-of-bounds read. The "hot path" comment does not justify removing a bounds check on untrusted input. Use `self.slots.get(slot).copied().flatten()`.

**`append_batch`, L193–196.** The pointer `first` is taken at L194, then `extend_from_slice` at L195 can reallocate `buf`. The read at L196 is then a use-after-free. The pointer is also unnecessary, because the first value is simply `batch[0]`. Rewrite as:
```rust
let (&head, _) = batch.split_first()?;
buf.extend_from_slice(batch);
Some((head, buf.len()))
```

**`decode`, L218.** `from_utf8_unchecked` runs on bytes from the network. Invalid UTF-8 produces a `String` that violates its invariants, which is UB. Use `std::str::from_utf8(&rest[..len]).map_err(|_| InvError::Malformed("invalid utf-8"))?`.

## Panics and wrong results

**`deltas`, L156–157.** The loop runs `i` over `0..prices.len()`, so on the last iteration `prices[i + 1]` is `prices[len]`, which is out of bounds. Every non-empty input panics, including `deltas(&[5])`. Use `prices.windows(2).map(|w| w[1] - w[0]).collect()`, or fix the range to `0..prices.len().saturating_sub(1)`. The subtraction can also overflow `i64` for extreme prices (L157).

**`available()`, L47.** Once `reserved > on_hand` (reachable through `record_loss`), this underflows. Debug builds panic; release builds wrap to about 4 billion, so `reserve()` at L92 accepts any quantity and oversells.

**`record_loss`, L120.** `on_hand -= lost` is unchecked, so `lost > on_hand` underflows. It also leaves `reserved > on_hand`, which breaks the invariant that `available()` relies on. Reject losses greater than `on_hand` with an error, and decide explicitly how a loss interacts with existing reservations.

**`ship`, L112.** `on_hand -= qty` underflows whenever the invariant has already been broken by `record_loss`. Example: `on_hand = 5, reserved = 5`, then `record_loss(3)` gives `on_hand = 2, reserved = 5`, and `ship(5)` panics in debug. Fixing `record_loss` fixes this path, but `ship` should use checked arithmetic too.

**`receive`, L80–81.** The doc says units are added to an existing SKU, but `insert` replaces the whole item. `on_hand` becomes `qty`, `reserved` becomes 0, and the price is overwritten. Any live holds on that SKU are now unbacked, so a later `confirm` fails with `Insufficient` after the hold has already been removed. Update the existing entry instead, e.g. `items.entry(sku)` with `on_hand.checked_add(qty)`.

**`encode`, L204.** `name.len() as u8` truncates names over 255 bytes, but all the bytes are still written. The length prefix then disagrees with the payload, and the receiver misframes the record. Return an error for long names, or truncate on a character boundary.

**`place_hold`, L253.** `Instant::now() + ttl` panics if the sum overflows, which a large caller-supplied `ttl` can trigger. Use `checked_add` and return an error.

**`total_value`, L127.** `on_hand as u64 * price_cents` and the `sum` are unchecked. This is unlikely with realistic values but panics in debug and wraps in release.

**`release`, L101.** `saturating_sub` silently accepts over-release. That hides mismatches between holds and reservations, which is how the `receive` problem above would go unnoticed. Consider returning an error when `qty > reserved`.

## Concurrency

**Deadlock between `place_hold` and `confirm`.** `place_hold` locks `warehouse` (L245) then `holds` (L247). `confirm` locks `holds` (L259) then `warehouse` (L262 or L265). If one thread is in each function, both block forever. `sweep_expired` uses the same order as `place_hold`, so `confirm` is the outlier. Standardise on one order everywhere, and ideally drop the lock before taking the other one.

## Checked and found fine

- The `try_into().unwrap()` calls in `decode` are safe because the length check at L215 guarantees the slices are 4 bytes.
- `sweep_expired` discards `release` errors, but the only error case is an unknown SKU, which a hold cannot reference.
- `parse_command` and the `Warehouse` read paths have no defects beyond those listed above.

The existing tests cover none of the failing paths above. A `deltas` test on a non-empty slice would have caught the panic immediately.

ISSUES:
L185: SlotTable::lookup uses get_unchecked on an untrusted slot index (out-of-bounds read, UB)
L196: append_batch dereferences a pointer that extend_from_slice may have invalidated (use-after-free)
L218: from_utf8_unchecked on untrusted network bytes (UB and invalid String)
L157: off-by-one index, prices[i + 1] reads past the end; panics on every non-empty input
L157: i64 subtraction can overflow for extreme prices (panic in debug, wrap in release)
L245: place_hold locks warehouse then holds, while confirm (L259, then L262/L265) locks holds then warehouse; AB-BA deadlock
L80: receive replaces the existing item, resetting on_hand to qty and reserved to 0, contrary to its doc
L120: record_loss subtracts without a check; can underflow and leave reserved above on_hand
L112: ship subtracts from on_hand without a check; underflows once on_hand < reserved
L47: available() underflows when reserved > on_hand; panics in debug, wraps to a huge value in release, allowing oversell
L204: names over 255 bytes truncate the length prefix, producing a corrupt wire record
L253: Instant::now() + ttl panics on overflow for very large ttl
L127: total_value multiplication and sum are unchecked
L101: release silently accepts over-release, hiding hold/reservation mismatches