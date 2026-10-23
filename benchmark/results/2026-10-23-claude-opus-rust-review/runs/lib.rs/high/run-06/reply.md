# Review of `src/lib.rs`

The module has four sources of undefined behaviour, one deadlock, and several logic errors and panics. Grouped by severity:

## Undefined behaviour (memory safety)

**L185 – `SlotTable::lookup` uses `get_unchecked` on untrusted input.** The doc comment says `slot` comes straight from a scanner message. Any out-of-range value reads past the end of the `Vec`. That is UB, not a panic. A bounds check is not worth removing here. Use `self.slots.get(slot).copied().flatten()`.

**L194–196 – `append_batch` reads through a dangling pointer.** `first` is taken from `buf.as_ptr()`. Then `extend_from_slice(tail)` can reallocate the buffer, and `*first` reads freed memory. `wrapping_add` does not help. The value is already known (`head`), so return `head`. Or read `buf[start]` after the extend.

**L218 – `decode` calls `from_utf8_unchecked` on network data.** Invalid UTF-8 inside a `String` is UB, and later string operations can misbehave arbitrarily. Use `std::str::from_utf8(...).map_err(|_| InvError::Malformed("bad utf-8"))?`.

## Concurrency

**L245–247 / L259–265 / L272–273 – inconsistent lock order causes deadlock.** `place_hold` and `sweep_expired` lock `warehouse` then `holds`. `confirm` locks `holds` then `warehouse`. If `confirm` runs at the same time as either of the others, each thread can hold one lock while waiting for the other. Pick one order everywhere, e.g. always `warehouse` before `holds`.

**L265–266 – a failed `confirm` leaks the reservation.** The hold is removed at L260 before `ship` runs. If `ship` fails, the reserved units are never released and the hold cannot be retried. This can happen after the `receive` bug below resets `reserved`. Remove the hold only after `ship` succeeds, or release on failure.

**L253 – `Instant::now() + ttl` panics on overflow.** A very large caller-supplied `ttl`, such as `Duration::MAX`, panics while the warehouse lock is held. The stock is already reserved by then and is never released, and the mutexes become poisoned. Use `checked_add` and return an error.

## Logic errors and arithmetic panics

**L79–81 – `receive` replaces the item instead of adding to it.** The doc says units are added to existing stock, but `insert` overwrites the item. That discards existing `on_hand` and also resets `reserved` to 0 while holds are still outstanding. Those holds then fail to ship, or are silently "released" by `saturating_sub`. Use `entry(sku)` and add `qty` with a checked add, keeping `reserved`.

**L120 – `record_loss` does an unchecked subtraction and breaks the invariant.** If `lost > on_hand`, it underflows: a panic in debug, a wrap to about 4 billion in release. Even when it doesn't underflow, it can push `on_hand` below `reserved`. Validate `lost <= on_hand` and decide how to handle reserved units, for example by capping `reserved` or rejecting the call.

**L47 – `available()` underflows once `reserved > on_hand`.** Through the `record_loss` path above, this panics or wraps. Since `reserve` (L91) and `low_stock` (L132–133) call it, a wrapped value lets `reserve` over-commit stock.

**L112 – `ship` decrements `on_hand` unchecked.** It only checks `qty <= reserved`. When `on_hand < reserved` (again via `record_loss`), this underflows.

**L127 – `total_value` can overflow.** `on_hand as u64 * price_cents` and the `.sum()` can both overflow u64 with large prices or quantities. Use `u128`, or `checked_mul` / `checked_add`.

**L156–157 – `deltas` indexes out of bounds.** The loop runs `i` up to `len - 1` and reads `prices[i + 1]`, so it panics on every non-empty input. Use `prices.windows(2).map(|w| w[1] - w[0])`. The `i64` subtraction can also overflow for extreme values; use `checked_sub` if that matters.

**L204 – `encode` truncates name lengths.** `name.len() as u8` wraps for names of 256 bytes or more. The length prefix no longer matches the bytes written, so `decode` returns the wrong name, SKU, and quantity with no error. Reject or truncate long names explicitly, and make `encode` fallible.

## Lower-severity note

`release` (L101) uses `saturating_sub`, which hides over-release bugs like the `receive` reset above. Consider returning `Insufficient` instead. I haven't listed it as a defect.

ISSUES:
L185: `get_unchecked` on untrusted scanner slot index — out-of-bounds read is UB
L196: dangling pointer read after `extend_from_slice` may reallocate the Vec (use-after-free)
L218: `from_utf8_unchecked` on network bytes — invalid UTF-8 in String is UB
L259: `confirm` locks holds→warehouse while `place_hold`/`sweep_expired` lock warehouse→holds — ABBA deadlock
L266: hold removed before `ship`; if ship fails the reservation leaks and the hold is lost
L253: `Instant::now() + ttl` panics on overflow with large ttl after stock already reserved (poisons mutexes)
L81: `receive` overwrites existing item instead of adding qty, and resets `reserved` to 0 under live holds
L120: `record_loss` unchecked subtraction underflows and can drive `on_hand` below `reserved`
L47: `available()` underflows (panic/wrap) when `reserved > on_hand`, letting `reserve` over-commit
L112: `ship` decrements `on_hand` unchecked — underflows when `on_hand < reserved`
L127: `total_value` multiplication/sum can overflow u64
L157: `deltas` reads `prices[i + 1]` past the end — always panics on non-empty input
L204: `name.len() as u8` truncates names ≥256 bytes, producing corrupt records that decode wrongly