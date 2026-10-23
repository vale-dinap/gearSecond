I read the module without compiling or running it, so these findings come from reading the code. The most serious problems are the unsound `unsafe` blocks, a lock-order deadlock, and a `deltas` function that always panics.

## Undefined behaviour and memory safety

- **`lookup` (L185)** is a safe function that calls `get_unchecked` on an index that comes from a scanner message. An out-of-range slot is an out-of-bounds read. The bounds check is cheap, so use `self.slots.get(slot).copied().flatten()`. If the unchecked path is truly needed, make the function `unsafe` and document the contract.
- **`append_batch` (L194–196)** takes `first` as a pointer into `buf` before `extend_from_slice`. The extend can reallocate, which leaves `first` dangling, so `*first` is a use-after-free. The `unsafe` is unnecessary: the first SKU is `head`, so return that directly.
- **`decode` (L218)** calls `from_utf8_unchecked` on bytes from the network. Any sender can produce an invalid `String`, which is UB. Use `std::str::from_utf8(...).map_err(|_| InvError::Malformed("bad utf-8"))?`.

## Concurrency

- **Lock-order inversion (L259).** `confirm` locks `holds` and then `warehouse`. `place_hold` (L245, L247) and `sweep_expired` (L272–273) lock `warehouse` and then `holds`. Thread A in `confirm` and thread B in `place_hold` can each hold one lock and wait forever for the other. Pick one order and use it everywhere, or merge the two maps under one mutex.
- **Lock poisoning.** Every `lock().unwrap()` turns one panic into a permanent failure of the service. Consider handling poisoned locks explicitly.

## Integer arithmetic

- **Root cause at `record_loss` (L120).** It subtracts `lost` from `on_hand` without checking, so it can underflow. It also doesn't keep `reserved <= on_hand`, which the rest of the code assumes.
- **`available` (L47)** then computes `on_hand - reserved` on a state that can violate that invariant. In debug builds this panics. In release builds it wraps to about 4 billion, so `reserve` accepts any quantity and oversells.
- **`ship` (L112)** has the same underflow on `on_hand` after a loss.
- **`total_value` (L127)** multiplies and sums in `u64` without checks. Use `checked_mul` and `checked_add`, or saturating ops, and report overflow.
- **`deltas` (L157)** also has `i64` subtraction that can overflow at extreme values. Prices are cents and unlikely to reach that, so this is minor.

## Logic

- **`deltas` (L157)** indexes `prices[i + 1]` on the last iteration, when `i + 1 == prices.len()`. Any non-empty input panics. Replace the loop with `prices.windows(2).map(|w| w[1] - w[0]).collect()`.
- **`receive` (L80–81)** calls `insert`, which replaces the existing entry. The doc says units are added to existing stock, but `on_hand` is discarded and `reserved` is reset to 0. Live holds still count units that no longer exist, so a later `confirm` can ship stock that was never reserved. Use `entry(sku)` and add to `on_hand` with a checked add.
- **`encode` (L204)** uses `name.len() as u8`. A name of 256 bytes writes length 0, and the frame is then corrupt for any reader. Return an error for names over 255 bytes.

## Lower-severity notes (not in the ISSUES list)

- In `confirm` (L262–266), the hold is removed before `ship` runs. If `ship` ever fails, the hold is lost and its reservation leaks. This is latent because the `Service` API keeps the reserved counts balanced, but moving the removal after success is safer.
- `sweep_expired` (L278) discards the `release` error and still drops the hold.
- `log` (L69) grows without limit in a long-running process, and `reserve`/`release` are not logged.
- The existing tests cover none of these paths. Add tests for `deltas` on `[1, 2]`, `record_loss` beyond `on_hand`, a 256-byte name in `encode`, and invalid UTF-8 in `decode`.

ISSUES:
L47: available() underflows when reserved > on_hand (reachable via record_loss); reserve() then oversells in release builds
L80: receive() replaces the existing item, zeroing reserved and discarding on_hand, contrary to its doc
L112: ship() can underflow on_hand after a loss
L120: record_loss() subtracts without a check, underflowing on_hand
L127: total_value() multiplication and sum can overflow u64
L157: deltas() reads prices[i + 1] past the end on the last iteration; panics on any non-empty input
L185: lookup() uses get_unchecked on an untrusted index; out-of-bounds read is UB
L196: append_batch() dereferences a pointer that extend_from_slice may have invalidated; use-after-free
L204: encode() casts name length with `as u8`, so names over 255 bytes corrupt the frame
L218: decode() calls from_utf8_unchecked on network bytes; invalid UTF-8 yields an invalid String
L259: confirm() locks holds then warehouse, the opposite of place_hold/sweep_expired; deadlock