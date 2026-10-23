I read the module without compiling or running it, so these are findings from inspection. The `unsafe` blocks are the most urgent. The `deltas` panic is the most obvious bug, since it fires on any non-empty input and the existing tests don't exercise it.

## Undefined behaviour

- **`SlotTable::lookup` (L183-186):** `get_unchecked` is called with `slot` from a scanner message, which is untrusted. An out-of-range slot is an out-of-bounds read. Use `self.slots.get(slot).copied().flatten()`. The "hot path" comment doesn't justify removing the check on untrusted input.
- **`decode` (L218):** `from_utf8_unchecked` on network bytes is UB when the bytes aren't valid UTF-8. Use `std::str::from_utf8` and map the error to `InvError::Malformed`.
- **`append_batch` (L194-196):** The pointer is taken before `extend_from_slice`, which can reallocate `buf`. Dereferencing it afterwards is a use-after-free. The value is already known, so return `head` directly and drop the pointer code.

## Panics

- **`deltas` (L156-157):** The loop runs `i` over `0..prices.len()` and reads `prices[i + 1]`. On the last iteration that index is `len`, which is out of bounds, so any non-empty input panics. Use `prices.windows(2).map(|w| w[1] - w[0]).collect()`.
- **`deltas` subtraction (L157):** `i64` subtraction overflows for extreme prices. Debug builds panic and release builds wrap to a wrong value. Use `checked_sub` or document the input range.
- **`place_hold` (L253):** `Instant::now() + ttl` panics when `ttl` is very large. Use `checked_add` and return an error.

## Integer arithmetic

- **`Item::available` (L47):** `on_hand - reserved` underflows once `reserved > on_hand`. `record_loss` can cause that state (see below). Debug builds panic and release builds report a huge available count, which allows overselling. `low_stock` (L132) inherits the same problem.
- **`record_loss` (L120):** `on_hand -= lost` is unchecked. Losing more than is on hand underflows, and the reserved count isn't adjusted when reserved units are lost.
- **`ship` (L112):** `on_hand -= qty` can underflow for the same reason, because the check at L108 only looks at `reserved`.
- **`total_value` (L127):** `on_hand as u64 * price_cents` and the `sum()` can overflow. `receive` doesn't bound `price_cents`, so large values are reachable. Use `checked_mul` / `checked_add` or `saturating_*`.

## Concurrency

- **Lock-order inversion (L259 vs L245-247):** `place_hold` takes `warehouse` then `holds`. `confirm` takes `holds` (L259) and then `warehouse` (L262/L265). If one thread is in `place_hold` and another in `confirm`, they can deadlock. `sweep_expired` (L272-273) uses the same order as `place_hold`, so it is consistent with it. Pick one global order and use it on every path, or merge the two maps under one lock.
- **Hold removed before a fallible operation (L260-266):** `confirm` removes the hold before the expiry check and `ship`. If `ship` returns `Insufficient`, the hold is gone and its reservation stays in the warehouse with no owner. Check and ship first, then remove the hold on success.
- **Lock poisoning (throughout, e.g. L245):** Every lock is `.unwrap()`ed. Once any of the panics above fires while a lock is held, every later call panics too. Fixing the panics mostly removes this risk, but it's worth knowing.

## Logic and data

- **`receive` (L79-81):** The doc says units are added to existing stock, but `insert` replaces the item. That resets `reserved` to 0 while active holds still exist, which overstates availability. It also overwrites the name and price.
- **`encode` (L204):** `name.len() as u8` silently truncates names longer than 255 bytes. The length prefix then disagrees with the bytes that follow, so the frame is corrupt. Return an error for names over 255 bytes.
- **`log` growth (L69):** Every operation appends a `String` that is never trimmed. A long-running service will grow without bound.

I found no issues in `moving_average`, `parse_command`, or the `Hold` and `Item` types beyond what's listed above.

ISSUES:
L185: `get_unchecked` on untrusted slot index is an out-of-bounds read (UB)
L196: stale pointer dereferenced after `extend_from_slice` may reallocate (use-after-free, UB)
L218: `from_utf8_unchecked` on untrusted network bytes (UB on invalid UTF-8)
L156: `deltas` indexes `prices[i + 1]` past the end; panics on any non-empty input
L157: `deltas` i64 subtraction overflows for extreme prices
L47: `available()` underflows when reserved exceeds on_hand
L120: `record_loss` underflows `on_hand` and does not adjust `reserved`
L112: `ship` can underflow `on_hand` once the reserved/on_hand invariant is broken
L127: `total_value` multiplication and sum can overflow
L253: `Instant + ttl` panics on a very large ttl
L259: `confirm` takes holds then warehouse lock, inverting `place_hold` order (deadlock)
L260: `confirm` removes the hold before a fallible `ship`, leaking the reservation on error
L81: `receive` replaces existing SKU, resetting reserved and contradicting its doc
L204: `encode` truncates names over 255 bytes, corrupting the frame
L69: `Warehouse::log` grows without bound