I read the module without compiling it or running tests, so these findings come from reading the code. The worst problems are a guaranteed panic in `deltas`, undefined behaviour in `lookup`, `decode` and `append_batch`, and a lock-order deadlock between `place_hold` and `confirm`.

## Memory safety and undefined behaviour

- **`lookup` (L185):** `get_unchecked` runs on a slot index that comes from a scanner message, so an out-of-range value is undefined behaviour. The "hot path" comment does not justify it. Use `self.slots.get(slot).copied().flatten()`.
- **`decode` (L218):** `from_utf8_unchecked` runs on untrusted network bytes. Invalid UTF-8 is undefined behaviour. Use `std::str::from_utf8` and map the error to `Malformed`.
- **`append_batch` (L194–197):** `first` is a raw pointer taken before `extend_from_slice`. That call can reallocate `buf`, and the dereference at L196 then reads freed memory. The first SKU is just `head`, so return `head` and drop the pointer entirely.

## Panics and logic errors

- **`deltas` (L156–157):** the loop runs `i` over `0..prices.len()`, so `prices[i + 1]` reads one past the end on the last iteration. Every non-empty input panics, and the module has no test for it. Use `prices.windows(2).map(|w| w[1] - w[0])`, or loop over `0..prices.len() - 1`. The subtraction can also overflow `i64` for extreme prices, so use `checked_sub` if that matters.
- **`receive` (L80–81):** the doc says units are added to existing stock, but `insert` replaces the whole item. That resets `on_hand` to `qty` instead of adding, zeroes `reserved` while holds still exist, and overwrites the name and price. Use `entry(sku)` and add `qty` to `on_hand`.
- **`record_loss` (L120):** nothing checks `lost` against stock, so `on_hand -= lost` can underflow. It also ignores reservations, so `on_hand` can drop below `reserved`. After that, `available()` (L47) underflows, which panics in debug and wraps in release, and `reserve` then makes wrong decisions. Reject losses above `on_hand - reserved`.
- **`available` (L47):** `on_hand - reserved` assumes `reserved <= on_hand`, and nothing maintains that once `record_loss` runs. `low_stock` (L132) and `reserve` (L91) depend on it.
- **`encode` (L204):** `name.len() as u8` silently truncates names over 255 bytes. The length prefix then disagrees with the payload and the frame is corrupt. Return an error for long names.
- **`total_value` (L127):** `on_hand as u64 * price_cents` and the `sum()` can overflow `u64`. Realistic prices can reach that. Use `checked_mul` and `checked_add`, or accumulate in `u128`.
- **`confirm` (L259–266):** the hold is removed from the map before `ship` runs. If `ship` fails, the reservation is never released and the hold is gone. Reaching this path needs the `receive` bug above, but the ordering is still wrong. Look up the hold, call `ship`, and remove the hold only on success.
- **`place_hold` (L253):** `Instant::now() + ttl` panics if `ttl` is large enough to overflow the clock. Use `checked_add` and return an error.

## Concurrency

- **Deadlock:** `place_hold` takes `warehouse` (L245) then `holds` (L247). `sweep_expired` (L272–273) follows the same order. `confirm` takes `holds` (L259) and then `warehouse` (L262, L265), which is reversed. If one thread is in `place_hold` and another is in `confirm`, each can hold one lock and wait for the other. Pick one global order and use it everywhere, or take `holds` before `warehouse` in all three.
- `next_id` gets its own mutex, which is unnecessary. Keep it under the `holds` lock. Every `unwrap()` on a lock also turns one panic into a poisoned-lock panic for all later callers. That is a design choice to make, not a bug on its own.

## Smaller points

- `moving_average` (L144) panics on `window == 0`, which is a public API panic. Returning a `Result` or documenting it would help.
- `log` (L69) grows without bound on a long-running service.
- `sweep_expired` (L278) discards the `release` result with `let _`. It is harmless now because SKUs are never removed, but a comment would say so.

ISSUES:
L47: `available()` underflows when `reserved > on_hand`, which `record_loss` can cause
L80: `receive` overwrites the item instead of adding to `on_hand`, resets `reserved`, and replaces name and price
L120: `record_loss` can underflow `on_hand` and ignores reserved units
L127: `total_value` overflows u64 in the multiply and the sum
L157: `deltas` indexes `prices[i + 1]` out of bounds on the last iteration, so every non-empty input panics
L185: `lookup` uses `get_unchecked` on an untrusted index, which is undefined behaviour
L195: `append_batch` reads through a pointer taken before `extend_from_slice` may reallocate, which is use-after-free
L204: `encode` truncates names longer than 255 bytes into a corrupt frame
L218: `decode` uses `from_utf8_unchecked` on untrusted bytes, which is undefined behaviour
L253: `Instant::now() + ttl` can panic on overflow
L259: `confirm` takes holds then warehouse, the reverse of `place_hold` and `sweep_expired`, so the two can deadlock
L266: `confirm` removes the hold before `ship` succeeds, so a failed ship leaks the reservation