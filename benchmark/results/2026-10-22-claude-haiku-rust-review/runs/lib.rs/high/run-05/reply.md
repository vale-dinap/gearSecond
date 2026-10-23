I reviewed this by reading it. I didn't compile it or run it. The most serious problems are undefined behaviour in three `unsafe` spots, and `deltas` panics on every non-empty input.

## Memory safety and undefined behaviour

- **`SlotTable::lookup` (L185):** `get_unchecked` is called with a slot index from a scanner message, which is untrusted. Any `slot >= len` is out-of-bounds UB. The "hot path" comment doesn't justify it, and `self.slots.get(slot).copied().flatten()` costs essentially nothing.
- **`append_batch` (L194–196):** The pointer `first` is taken before `extend_from_slice`, which can reallocate `buf`. Dereferencing `first` afterwards reads freed memory whenever the buffer grows. The `unsafe` is also unnecessary, because the value at `buf[start]` is just `head`. Replace the body with `Some((head, buf.len()))`. Running `cargo miri test` on the original would show the bug.
- **`decode` (L218):** `from_utf8_unchecked` runs on bytes from the network. Invalid UTF-8 produces a `String` that violates its invariant. Use `std::str::from_utf8(...)` and map the error to `Malformed`.

## Panics and wrong results

- **`deltas` (L156–157):** The loop runs `0..prices.len()` and reads `prices[i + 1]`. At `i = len - 1` that index is out of bounds, so any non-empty input panics. `prices.windows(2).map(|w| w[1] - w[0]).collect()` fixes this. The `i64` subtraction can still overflow for extreme values, so use `checked_sub` if that matters.
- **`record_loss` (L120) and `available` (L47):** Nothing checks `lost <= on_hand`, and nothing checks reserved against the new on-hand count. One loss can leave `on_hand < reserved`. After that, `available()` panics in debug builds. In release builds it wraps to about 4 billion, so `reserve` would accept oversized quantities. `ship` (L112) can underflow for the same reason.
- **`receive` (L81):** The doc says units are added to an existing SKU, but `insert` replaces the whole item. On-hand is set to `qty`, reserved is reset to 0, and name and price are overwritten. Existing holds become untracked, so later `ship` or `release` calls see inconsistent counts. Use `entry` and `on_hand = on_hand.checked_add(qty)`.
- **`total_value` (L127):** `on_hand as u64 * price_cents` and the `sum` can overflow `u64` for large prices. Use `checked_mul` and `checked_add`, or `u128`.
- **`place_hold` (L253):** `Instant::now() + ttl` panics when `ttl` is very large, and `ttl` comes from the caller. Use `checked_add` and return an error.
- **`encode` (L204):** `name.len() as u8` silently truncates names longer than 255 bytes. The length byte then disagrees with the name bytes, and the receiver misparses the SKU and quantity. Return an error for names over 255 bytes.

## Concurrency

- **Lock-order inversion:** `place_hold` (L245–247) and `sweep_expired` (L272–273) lock the warehouse and then the holds. `confirm` (L259, then L262/L265) locks the holds and then the warehouse. A `place_hold` running alongside a `confirm` can deadlock. Pick one order everywhere, or put both pieces of state behind one lock.
- **Lost reservations in `confirm` (L260–266):** The hold is removed from the map before `ship` runs. If `ship` fails, the hold is gone, but its units stay reserved forever.
- **Lock poisoning:** Every `lock().unwrap()` turns one panic (such as the overflows above) into a panic on every later request. Handle `PoisonError` or remove the panics.

## Smaller points

- `release` (L101) saturates, so releasing more than was reserved succeeds silently and hides double-release bugs.
- `decode` ignores trailing bytes. If frames are per-message, check the exact length.
- `moving_average` panics on `window == 0`. That's documented, but it's a panic on caller input.
- `Warehouse::log` grows without bound in a long-running service.
- The tests cover only the happy path. None of them exercise restocking, losses, multiple SKUs, invalid UTF-8, names over 255 bytes, short price slices, or concurrency.

ISSUES:
L47: available() subtracts unchecked; panics in debug and wraps in release when reserved > on_hand
L81: receive replaces an existing SKU, resetting on_hand and reserved instead of adding to them
L120: record_loss subtracts without checking lost <= on_hand, can break reserved <= on_hand
L127: total_value multiplication and sum can overflow u64
L157: deltas reads prices[i + 1] out of bounds, panics on every non-empty input
L185: lookup uses get_unchecked on an untrusted slot index (out-of-bounds UB)
L196: append_batch dereferences a pointer that extend_from_slice can invalidate (use-after-free UB)
L204: encode truncates name length to u8 for names over 255 bytes
L218: decode uses from_utf8_unchecked on network bytes (UB on invalid UTF-8)
L253: place_hold computes Instant + ttl unchecked, panics on large ttl
L259: confirm locks holds then warehouse, while place_hold and sweep_expired lock warehouse then holds (deadlock)
L266: confirm removes the hold before ship; if ship fails, the reservation is leaked