I reviewed this by reading it. I did not compile it or run the tests, so the panic and overflow claims are from reasoning about the code. The existing tests don't exercise any of the defects below.

## Undefined behaviour (fix first)

**`SlotTable::lookup` (L185).** `get_unchecked` is called with `slot`, which the comment says comes from a handheld scanner, so it is untrusted. Any `slot >= slots.len()` is an out-of-bounds read. Use `self.slots.get(slot).copied().flatten()`. The "hot path" savings aren't worth it here.

**`decode` (L218).** `from_utf8_unchecked` runs on bytes from the network. Invalid UTF-8 produces a `String` that violates its invariants, which is UB. Use `std::str::from_utf8(...)` and map the error to `InvError::Malformed`.

**`append_batch` (L194–196).** `first` is a raw pointer into `buf` taken before `extend_from_slice(tail)`. That call can reallocate, which leaves `first` dangling, and `*first` is then a use-after-free. The pointer is also unnecessary: the value is just `head`. Return `Some((head, buf.len()))`.

## Panics

**`deltas` (L156–157).** The loop runs `i` over `0..prices.len()` but reads `prices[i + 1]`, so the final iteration indexes `prices[len]`. Any non-empty input panics, including `deltas(&[1])`. Loop over `0..prices.len().saturating_sub(1)`, or use `prices.windows(2)`.

**`Service::place_hold` (L253).** `Instant::now() + ttl` panics if the sum overflows, for example with `Duration::MAX`. Use `checked_add` and return an error.

## Deadlock

**Lock order inversion in `confirm` (L259).** `confirm` locks `holds` and then `warehouse` (L262, L265). `place_hold` (L245, L247) and `sweep_expired` (L272–273) lock `warehouse` and then `holds`. Thread A in `confirm` holding `holds` and waiting on `warehouse`, while thread B in `place_hold` holds `warehouse` and waits on `holds`, is a deadlock. Pick one global order, or put the warehouse and holds behind a single mutex.

## Logic errors

**`receive` on an existing SKU (L81).** The doc says units are added to stock, but `insert` replaces the whole `Item`. That resets `reserved` to 0 and discards `on_hand`, `name` and `price`. Outstanding holds stay in `Service::holds`, but the warehouse no longer knows about them, so the same units can be promised twice. Use `entry(sku).and_modify(...).or_insert_with(...)`.

**`confirm` loses the hold on a failed ship (L260).** The hold is removed from the map before `ship` runs. If `ship` returns `Insufficient`, the hold is gone and its units are never released. This becomes reachable once `receive` or `record_loss` has broken the reserved/on-hand invariant. Check the stock first, or re-insert the hold on error.

**`record_loss` breaks the invariant (L120).** It does `on_hand -= lost` with no check. It can push `on_hand` below `reserved`, which underflows in debug builds. In release it wraps to about 4 billion units. The check should be `lost <= on_hand - reserved` and the function should return `Insufficient` otherwise.

**`available()` underflow (L47).** `on_hand - reserved` assumes `reserved <= on_hand`, which `record_loss` can violate. In debug builds this panics. In release it wraps to a huge value, so `reserve` will accept orders far beyond stock. `low_stock` (L132) and `reserve` (L91) both depend on this.

**`release` saturates (L101).** `saturating_sub` hides over-release, which is exactly how the invariant problems above go unnoticed. Consider returning an error when `qty > reserved`.

## Overflow

**`total_value` (L127).** `on_hand as u64 * price_cents` can overflow for large prices and quantities, and the `sum()` can overflow too. Use `checked_mul` and `checked_add`, or `saturating_*`, and make the result an `Option` or `Result`.

## Wire format

**`encode` truncates names (L204).** `name.len() as u8` silently wraps for names over 255 bytes. The length byte then disagrees with the payload, and the receiver misparses everything after it. Reject names longer than 255 bytes or truncate them on a character boundary, and return an error.

## Suggested tests

- `deltas(&[1])` and `deltas(&[1, 2, 3])`
- `receive` on an existing SKU after a reservation, then `confirm`
- `record_loss` larger than available stock
- `decode` with invalid UTF-8
- `lookup` with an out-of-range slot
- A two-thread test of `confirm` against `place_hold`

ISSUES:
L47: available() underflows when reserved > on_hand, wrapping in release builds and overselling
L81: receive() replaces the existing Item, resetting reserved and discarding on_hand, name and price; the doc says units are added
L101: release() uses saturating_sub, which hides over-release and masks invariant violations
L120: record_loss() subtracts without checking stock, so on_hand can drop below reserved or underflow
L127: total_value() multiplication and sum can overflow u64
L156: deltas() reads prices[i + 1] with i up to len-1, so every non-empty input panics out of bounds
L185: lookup() uses get_unchecked on an untrusted scanner slot index, an out-of-bounds read (UB)
L196: append_batch() dereferences a raw pointer that dangles if extend_from_slice reallocates (use-after-free)
L204: encode() casts name length to u8 without a check, corrupting frames for names over 255 bytes
L218: decode() calls from_utf8_unchecked on untrusted network bytes (UB on invalid UTF-8)
L253: place_hold() Instant + ttl panics on overflow for very large durations
L259: confirm() takes holds then warehouse, inverting the warehouse-then-holds order used elsewhere (deadlock)
L260: confirm() removes the hold before ship(); a failed ship loses the hold and its units are never released