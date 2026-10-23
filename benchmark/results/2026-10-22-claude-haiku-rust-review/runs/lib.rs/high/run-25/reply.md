I reviewed this by reading it. I haven't compiled it or run the tests. Findings are grouped by severity.

## Undefined behaviour

**`SlotTable::lookup` (L185).** `get_unchecked` takes `slot`, which the doc comment says comes straight from a scanner message. Any out-of-range slot is an out-of-bounds read, which is UB. The "hot path" justification doesn't hold for untrusted input. Use `self.slots.get(slot).copied().flatten()`.

**`append_batch` (L193–196).** `first` is a raw pointer to the head element, taken after `push`. `extend_from_slice(tail)` can reallocate the Vec, which leaves `first` dangling, and `*first` then reads freed memory. The read is also unnecessary, since the value is just `head`. Return `Some((head, buf.len()))` and drop the pointer code.

**`decode` (L218).** `from_utf8_unchecked` runs on bytes from the network. Invalid UTF-8 produces a `String` that violates its invariant, which is UB. Use `std::str::from_utf8(&rest[..len]).map_err(|_| InvError::Malformed("name not utf-8"))?`.

## Panics and arithmetic

**`deltas` (L156–157) panics on every non-empty input.** `for i in 0..prices.len()` runs `i` up to `len - 1`, so `prices[i + 1]` reads `prices[len]`. `[5]` panics immediately, and `[1, 2]` panics on the second iteration. Use `prices.windows(2).map(|w| w[1] - w[0]).collect()`. The subtraction can also overflow `i64` for extreme inputs, so `checked_sub` is worth considering.

**`Item::available` (L47) underflows.** `on_hand - reserved` wraps or panics when `reserved > on_hand`. That state is reachable through `record_loss` (L120), which can push `on_hand` below `reserved`. Then `reserve` (L91–95) sees a huge `have` and accepts more than exists, and `reserved += qty` can overflow. `low_stock` (L133) is also corrupted.

**`record_loss` (L120)** subtracts without checking `lost <= on_hand`. In debug it panics. In release it wraps to a huge stock count. It should return `Insufficient` and should not eat into reserved units.

**`ship` (L112)** does `on_hand -= qty` unchecked. It is safe only while `reserved <= on_hand` holds, and the bugs above break that invariant.

**`total_value` (L127)** can overflow `u64`, both in `on_hand as u64 * price_cents` and in `sum()`. Use `u128` or checked arithmetic.

**`place_hold` (L253)** computes `Instant::now() + ttl`, which panics if `ttl` is huge. Use `checked_add` and return an error.

## Logic

**`receive` (L80–81) contradicts its doc comment.** The doc says units are added to an existing SKU, but `HashMap::insert` replaces the whole item. `on_hand` becomes `qty`, `reserved` resets to 0, and name and price are overwritten. Holds that are still outstanding then point at reservations that no longer exist. Use `entry(sku).or_insert_with(...)` and add `qty` with `checked_add`. That changes the return type, so the signature needs to become `Result<(), InvError>`.

**`encode` (L204)** truncates with `name.len() as u8`. Names over 255 bytes produce a length prefix that disagrees with the body, and the receiver misparses everything after it. Use `u8::try_from(name.len())` and return an error.

**`release` (L101)** uses `saturating_sub`, which hides over-release. `confirm` (L262) and `sweep_expired` (L278, where the error is discarded with `let _`) both rely on it. A bookkeeping bug will go unnoticed.

## Concurrency

**Deadlock from lock-order inversion (L259–265).** `place_hold` locks `warehouse` (L245) and then `holds` (L247). `confirm` locks `holds` (L259) and then `warehouse` (L262, L265). `sweep_expired` (L272–273) follows the `place_hold` order. Thread A can hold `warehouse` in `place_hold` while waiting for `holds`, and thread B can hold `holds` in `confirm` while waiting for `warehouse`. Take the locks in one global order everywhere, for example `warehouse` before `holds`, which means `confirm` must lock `warehouse` first.

`unwrap()` on the locks means one panic (for example, from the arithmetic above) poisons the mutex and makes every later call panic. That may be acceptable, but it's worth knowing.

## Minor

- `log` (L69) grows without bound in a long-running service.
- `decode` (L212) silently accepts trailing bytes. If records are length-framed, check for an exact length.

The existing tests (L311–336) cover none of these cases. Add tests for the `deltas` panic, the `record_loss` underflow, the `receive` overwrite, and the concurrent `place_hold`/`confirm` path.

ISSUES:
L185: `get_unchecked` on a scanner-supplied slot index is an out-of-bounds read (UB)
L196: `first` pointer dangles after `extend_from_slice` may reallocate; reads freed memory (UB)
L218: `from_utf8_unchecked` on network bytes is UB for invalid UTF-8
L157: `deltas` indexes `prices[len]`; panics on every non-empty input
L47: `available()` underflows when `reserved > on_hand`
L120: `record_loss` subtracts without checking; underflow or wrap to huge stock
L112: `ship` subtracts from `on_hand` unchecked
L127: `total_value` u64 multiplication and sum can overflow
L80: `receive` overwrites an existing SKU instead of adding, and resets `reserved`
L204: name length truncated by `as u8`, corrupting the encoded record
L259: `confirm` locks `holds` before `warehouse`, inverting the `place_hold` order; deadlock
L253: `Instant::now() + ttl` panics on a huge TTL
L101: `release` saturates silently, masking over-release