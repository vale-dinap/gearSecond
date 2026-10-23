I reviewed the module by reading it. I did not compile or run it, so the points below come from the code alone. The most serious problems are an out-of-bounds read, a use-after-free, and a lock-order deadlock.

## Memory safety and undefined behaviour

- **`src/lib.rs:196` (`append_batch`)**: `first` points into `buf` as taken at line 194. `extend_from_slice` at line 195 can reallocate, which leaves `first` dangling, so `*first` is a use-after-free. The read is also unnecessary because `head` is already in scope. Fix: `Some((head, buf.len()))`, and remove the pointer and the `unsafe`.
- **`src/lib.rs:185` (`SlotTable::lookup`)**: `get_unchecked` is called with `slot` from a scanner message, so any out-of-range slot is an out-of-bounds read. A bounds check is one comparison and does not cost meaningful time on this path. `self.slots.get(slot).copied().flatten()` returns the same `Option<Sku>`.
- **`src/lib.rs:218` (`decode`)**: `from_utf8_unchecked` runs on network bytes. Invalid UTF-8 produces an invalid `String`, which is undefined behaviour as soon as anything uses it. Fix: `std::str::from_utf8(&rest[..len]).map_err(|_| InvError::Malformed("name is not UTF-8"))?`.

## Concurrency

- **Lock-order inversion (`src/lib.rs:259`, `262`, `265` against `245`/`247` and `272`/`273`)**: `place_hold` and `sweep_expired` lock `warehouse` before `holds`. `confirm` locks `holds` first (line 259), then `warehouse` (lines 262 and 265). If `place_hold` holds the warehouse lock while waiting for holds, and `confirm` holds holds while waiting for the warehouse, both threads deadlock. Fix: have `confirm` take `warehouse` first, and document one order.
- **Panic while locks are held (`src/lib.rs:253`)**: `Instant::now() + ttl` panics on overflow, for example if a caller passes `Duration::MAX`. By then `wh.reserve` at line 246 has already committed the reservation, so the stock stays reserved with no hold to release it. The panic also poisons both mutexes, and every later `.unwrap()` on them panics. Fix: compute `checked_add` before reserving and return an error.

## Logic errors

- **`src/lib.rs:81` (`receive`)**: The doc comment says units are added to an existing SKU, but `insert` replaces the whole `Item` and zeroes `on_hand` and `reserved`. Restocking silently discards stock and orphans active holds. Those holds then fail on `ship` or are silently saturated by `release`. Fix: use `entry(sku)` and add `qty` to `on_hand`.
- **`src/lib.rs:120` (`record_loss`)**: It never checks that `lost <= on_hand`, and it can consume units that are reserved for holds. That breaks the invariant `reserved <= on_hand`, which the next two items depend on.
- **`src/lib.rs:47` (`available`)**: `on_hand - reserved` underflows when `reserved > on_hand`, which `record_loss` can cause. In debug builds it panics. It is reached from `reserve`, from `low_stock` (line 132), and from the sort at line 133. In release builds it wraps to about 4 billion available units, which allows over-reservation.
- **`src/lib.rs:112` (`ship`)**: `on_hand -= qty` underflows under the same broken invariant.
- **`src/lib.rs:157` (`deltas`)**: The loop reads `prices[i + 1]` for `i` up to `len - 1`, so it indexes `prices[len]`. Every non-empty input panics; only `[]` works. The `with_capacity(len - 1)` on line 155 shows the loop was meant to run `len - 1` times. The subtraction can also overflow `i64` for extreme values. Fix: `prices.windows(2).map(|w| w[1] - w[0])`, with `checked_sub` if overflow matters.

## Overflow and data corruption

- **`src/lib.rs:127` (`total_value`)**: The `on_hand as u64 * price_cents` multiplication and the `sum()` are both unchecked. Large prices or many SKUs can overflow, which panics in debug and wraps in release. Use `checked_mul`/`checked_add` and return an error, or saturate.
- **`src/lib.rs:204` (`encode`)**: `name.len() as u8` truncates. A 256-byte name is written with length byte `0` followed by 256 name bytes, so the receiver misparses everything after it. `receive` places no limit on name length, so this is reachable. Fix: reject names longer than 255 bytes and return a `Result`.

## Design gaps (not counted as defects above)

- Expired holds are released only by `sweep_expired` or by `confirm` on that specific hold. Nothing calls the sweep automatically, so expired reservations keep blocking stock until someone runs it.
- `log` grows without bound in a long-running service. `reserve` and `release` are not logged at all, so the log is incomplete as an audit trail.
- Every lock uses `unwrap()`, so one panic while a lock is held takes the service down permanently. Fixing the panics above matters more than changing the unwrapping.

I found no defects in `moving_average` (its `assert!` is deliberate), `parse_command`, `decode`'s length checks, `snapshot`, or the `low_stock` sort. The existing tests cover reserve/ship and the codec round trip, but none of the paths above. Useful additions would be: loss followed by reserve, restock while holds are active, a 256-byte name, `deltas` on a one-element slice, and concurrent `place_hold` and `confirm`.

ISSUES:
L196: append_batch reads through a pointer that is dangling after extend_from_slice may reallocate (use-after-free)
L185: lookup uses get_unchecked on an untrusted slot index (out-of-bounds read, UB)
L218: decode uses from_utf8_unchecked on untrusted bytes (invalid String, UB)
L259: confirm locks holds before warehouse, inverting the place_hold/sweep_expired order (deadlock)
L253: Instant + ttl can panic after reserve has committed, leaking stock and poisoning both locks
L81: receive replaces an existing SKU, discarding on_hand and reserved and orphaning holds
L120: record_loss does not bound the loss by on_hand, breaking reserved <= on_hand
L47: available() underflows when reserved > on_hand (panic in debug, wrap in release)
L112: ship() on_hand subtraction can underflow under the same broken invariant
L157: deltas indexes prices[i + 1] out of bounds for i = len-1, panicking on any non-empty input
L127: total_value uses unchecked u64 multiplication and summation, which can overflow
L204: encode truncates the name length to u8, so names over 255 bytes produce corrupt records