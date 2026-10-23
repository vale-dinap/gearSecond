## Defects

### Undefined behaviour and memory safety

- **`SlotTable::lookup`, L185.** `get_unchecked` runs on a `slot` that comes from a scanner message. Any out-of-range slot is an out-of-bounds read, which is UB. Use `self.slots.get(slot).copied().flatten()`. The "hot path" comment doesn't justify the unsafe block.

- **`append_batch`, L194–197.** `first` points into `buf` before `extend_from_slice`. That call can reallocate, so `*first` reads freed memory. The function should return `buf[start]` after the extend, with no raw pointer at all.

- **`decode`, L218.** `from_utf8_unchecked` runs on bytes from the network. Invalid UTF-8 inside a `String` is UB. Use `std::str::from_utf8(...)` and map the error to `InvError::Malformed`.

### Panics and logic errors

- **`deltas`, L156–157.** The loop runs `i` over `0..prices.len()` and reads `prices[i + 1]`. On the last iteration that index is out of bounds, so every non-empty input panics. Use `prices.windows(2).map(|w| w[1] - w[0]).collect()`. The subtraction can also overflow `i64` for extreme prices, which `checked_sub` would catch.

- **`receive`, L81.** The doc says units are added to an existing SKU, but `insert` replaces the whole item. On-hand, reserved, name and price are all reset. Holds that are still outstanding then have no backing reservation, so a later `ship` can underflow or fail.

- **`record_loss`, L120.** `on_hand -= lost` has no check. It underflows when `lost > on_hand`, which panics in debug and wraps in release. It also ignores `reserved`, so `on_hand` can drop below `reserved`.

- **`available`, L47.** `on_hand - reserved` underflows once `reserved > on_hand`. The fields are `pub`, so callers can build that state, and `record_loss` above does. `reserve`, `low_stock` and `available` all hit this underflow. `available` should use `saturating_sub`, or the invariant should be enforced in one place.

- **`ship`, L112.** `on_hand -= qty` has the same underflow once the invariant is broken. It should use `checked_sub` and return an error.

- **`total_value`, L127.** `i.on_hand as u64 * i.price_cents` can overflow `u64`, and so can the `sum`. Use `checked_mul` and `checked_add`, or widen to `u128`.

- **`encode`, L204.** `name.len() as u8` truncates names longer than 255 bytes, but the full name is still written. The decoder then misreads the record. Reject names over 255 bytes with an error.

- **`confirm`, L266.** The hold is removed before `ship` runs. If `ship` fails, the reservation is never released and the units stay locked.

- **`release`, L101.** `saturating_sub` hides over-release. A release larger than the current reservation succeeds silently, which masks the bookkeeping bugs above.

- **`place_hold`, L253.** `Instant::now() + ttl` panics if the sum overflows, for example with `Duration::MAX`. Use `checked_add` and return an error.

### Concurrency

- **Lock-order inversion, L245–247 against L259–265.** `place_hold` and `sweep_expired` take `warehouse` then `holds`. `confirm` takes `holds` then `warehouse`. If one thread is in `confirm` and another is in `place_hold`, each can hold one lock while waiting for the other, which deadlocks. Pick one order everywhere, for example `warehouse` before `holds`, and restructure `confirm` to match.

## ISSUES:
L47: available() underflows when reserved > on_hand, reachable via record_loss; pub fields allow the invalid state
L81: receive() replaces existing item instead of adding stock as documented, resetting reserved and breaking outstanding holds
L101: release() saturating_sub silently hides over-release
L112: ship() on_hand -= qty underflows if invariant broken
L120: record_loss() on_hand -= lost underflows when lost > on_hand, no reserved check
L127: total_value() u64 multiply and sum can overflow
L157: deltas() indexes prices[i+1] past end, panics on every non-empty input; i64 subtraction can overflow
L185: lookup() get_unchecked on untrusted scanner slot, out-of-bounds read (UB)
L196: append_batch() dereferences pointer invalidated by extend_from_slice reallocation (use-after-free UB)
L204: encode() truncates name length to u8 for names over 255 bytes, producing corrupt records
L218: decode() from_utf8_unchecked on untrusted network bytes (UB on invalid UTF-8)
L253: place_hold() Instant + ttl panics on overflow
L259: lock-order inversion between confirm (holds→warehouse) and place_hold/sweep_expired (warehouse→holds), deadlock
L266: confirm() removes hold before ship; ship failure leaks the reservation