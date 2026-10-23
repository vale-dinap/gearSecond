I found several defects that should block the merge, including undefined behaviour on untrusted input, a guaranteed panic, and a lock-order deadlock. I reviewed by reading only. I did not compile, test, or run Miri on this code.

## Memory safety and undefined behaviour

**`SlotTable::lookup`, L185.** `get_unchecked(slot)` runs on a `slot` the doc comment says comes straight from a scanner message. Any out-of-range slot is an out-of-bounds read, which is UB. The "hot path" justification doesn't hold: the check is a single compare. Use `self.slots.get(slot).copied().flatten()`.

**`append_batch`, L194–197.** `first` is a raw pointer into `buf`'s allocation, taken before `extend_from_slice` at L195. That call can reallocate, which leaves `first` dangling, and L196 then dereferences it. The bug only shows up when the buffer grows, so tests with spare capacity will pass. The fix is to drop the pointer entirely and return `head`, which is the first SKU already.

**`decode`, L218.** `from_utf8_unchecked` runs on bytes that the doc says come from the network. Invalid UTF-8 produces a `String` that violates its invariants, which is UB. Use `std::str::from_utf8(...)` and map the error to `InvError::Malformed`.

## Panics

**`deltas`, L156–157.** The loop runs `i` over `0..prices.len()` but reads `prices[i + 1]`. For the last index that is `prices[len]`, which is out of bounds. Every non-empty input panics. The capacity on L155 shows the intent was `len - 1` iterations. Use `prices.windows(2).map(|w| w[1] - w[0])`, or `checked_sub` if overflow should be an error. The subtraction can also overflow `i64` on extreme inputs.

**`place_hold`, L253.** `Instant::now() + ttl` panics if the sum overflows, for example with a very large `Duration`. Use `checked_add` and return an error.

## Concurrency

**Lock-order inversion, L259 and L265.** `place_hold` (L245, L247) and `sweep_expired` (L272–273) take `warehouse` then `holds`. `confirm` takes `holds` (L259) and then calls `self.warehouse.lock()` (L262, L265) while still holding it. If one thread is in `confirm` and another is in `place_hold` or `sweep_expired`, each can wait on the other forever. Make `confirm` acquire `warehouse` first.

**Lock poisoning.** Every `.lock().unwrap()` turns one panic into a panic in every later caller. This is acceptable for a prototype, but it is worth a deliberate decision.

## Logic and invariant errors

**`Warehouse::receive`, L81.** `insert` replaces the existing item, which resets `on_hand` and `reserved` to zero. The doc comment on L77–78 says the units should be added. Replacing the item also orphans any live holds on that SKU, so a later `ship` either fails or consumes stock reserved for someone else. Fix it to add to the existing item. Use `checked_add`, which needs a `Result` return since the current signature cannot report overflow.

**`confirm`, L260 and L266.** The hold is removed from the map before `ship` runs. If `ship` returns `Insufficient`, the hold is gone but its reservation is still counted, so the stock stays locked permanently. Remove the hold only after `ship` succeeds.

**`record_loss`, L120.** `on_hand -= lost` has no check. It underflows and panics in debug, or wraps to about 4 billion units in release. It also ignores `reserved`, so `on_hand` can drop below `reserved`.

**`Item::available`, L47.** `on_hand - reserved` assumes `reserved <= on_hand`, which `record_loss` breaks. The underflow then propagates into `reserve`, which relies on `available()` for its capacity check, so release builds can over-reserve. Keep the invariant by having `record_loss` reject losses above `on_hand - reserved`, and consider `saturating_sub` only as a backstop.

**`total_value`, L127.** `on_hand as u64 * price_cents` and the `sum()` are unchecked. This needs very large prices or quantities to overflow, but a bad input can trigger it. Use `checked_mul` and `checked_add`.

**`encode`, L204.** `name.len() as u8` truncates names over 255 bytes while still writing all of the name. The length prefix then disagrees with the payload and the receiver misparses every field after it. Return an error on overlong names. This changes the signature to `Result<Vec<u8>, InvError>`.

## Not defects (checked)

- `moving_average`: the `assert!` on `window > 0` is a deliberate precondition, and the empty range for `window > len` is handled.
- `parse_command`: the bounds and trailing-input checks are correct.
- `snapshot` and the `Result::cloned` call compile as written, as far as I can tell.

## Recommended next steps

- Run `cargo test` and `cargo miri test`. Miri would catch the `append_batch` and `decode` UB directly.
- Add a stress test that runs `confirm` and `place_hold` concurrently to exercise the lock order.
- Add regression tests for `deltas` on a non-empty slice, `receive` on an existing SKU, and `confirm` after a failed `ship`.

ISSUES:
L185: `lookup` uses `get_unchecked` on an untrusted slot index, an out-of-bounds read (UB)
L196: `append_batch` dereferences a pointer that `extend_from_slice` may have invalidated by reallocating (use-after-free)
L218: `decode` uses `from_utf8_unchecked` on network input, so invalid UTF-8 is UB
L157: `deltas` indexes `prices[i + 1]` with `i` up to `len - 1`, panicking on every non-empty input
L157: `deltas` i64 subtraction can overflow on extreme values
L253: `Instant::now() + ttl` panics when the duration overflows the instant
L259: `confirm` takes `holds` then `warehouse`, inverting the lock order used elsewhere, so it can deadlock
L81: `receive` replaces an existing SKU instead of adding to it, resetting reserved units and orphaning holds
L260: `confirm` removes the hold before `ship`, so a failed ship leaks the reservation permanently
L120: `record_loss` subtracts without a check, underflowing and ignoring `reserved`
L47: `available()` underflows when `reserved > on_hand`, which `record_loss` can cause
L127: `total_value` multiplies and sums with unchecked u64 arithmetic
L204: `encode` truncates name lengths over 255 bytes, corrupting the frame