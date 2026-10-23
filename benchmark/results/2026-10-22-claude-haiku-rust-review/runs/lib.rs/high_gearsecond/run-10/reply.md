## Defects

**Undefined behaviour and memory safety**

- **`lookup`, L185:** `get_unchecked` runs on `slot`, which comes from an untrusted scanner message. Any `slot >= slots.len()` is an out-of-bounds read, which is UB. The "hot path" comment doesn't justify removing the check. Use `self.slots.get(slot).copied().flatten()`.
- **`append_batch`, L193-196:** `first` is computed from `buf.as_ptr()` before `extend_from_slice` at L195. That call can reallocate `buf`, so `first` dangles and the read at L196 is a use-after-free. The value is just `head`, so `first_val` can be `head` and the unsafe block can go.
- **`decode`, L218:** `from_utf8_unchecked` runs on bytes from the network. Invalid UTF-8 produces a `String` that violates its invariant, which is UB. Use `std::str::from_utf8(...).map_err(|_| InvError::Malformed("bad utf-8"))?`.

**Panics and integer overflow**

- **`deltas`, L156-157:** the loop runs `i` over `0..prices.len()`, so `prices[i + 1]` reads index `len` on the last iteration and panics. Any non-empty input with length 1 or more panics. Use `prices.windows(2).map(|w| w[1] - w[0])`. The subtraction can also overflow `i64` for extreme values, so consider `checked_sub` or documenting the range.
- **`record_loss`, L120:** `on_hand -= lost` is unchecked. Losing more than is on hand panics in debug builds and wraps to a huge value in release builds.
- **`record_loss` invariant, L120 and L47:** nothing stops `on_hand` from dropping below `reserved`. Once that happens, `available()` at L47 underflows, and `low_stock` (L132) and `reserve` (L91) hit the same underflow. Reject losses above `on_hand - reserved`, or check `on_hand >= reserved` after the change.
- **`available`, L47:** `on_hand - reserved` underflows whenever the invariant above is broken. Use `saturating_sub` as a fallback, but fix the invariant as well.
- **`total_value`, L127:** `on_hand as u64 * price_cents` and the `sum()` can overflow `u64`. Use `checked_mul`/`checked_add` or saturating arithmetic.
- **`place_hold`, L253:** `Instant::now() + ttl` panics for very large `Duration`s. Use `checked_add` and return an error.

**Logic errors**

- **`receive`, L79-81:** `insert` replaces the existing item. Its `reserved` resets to 0, and `on_hand` becomes `qty` rather than adding to it. The doc comment at L77-78 says units should be added. Outstanding holds then have no backing stock, so a later `confirm` fails at `ship`'s check (L108-110) after the hold was already removed. Fix: update the existing entry (`on_hand += qty`, keep `reserved`), and check that the addition doesn't overflow.
- **`encode`, L204:** `name.len() as u8` silently truncates names longer than 255 bytes. The length byte then disagrees with the payload, so the record is corrupt and `decode` misparses it. Return an error for names over 255 bytes, or validate the name when it is created.
- **`release`, L101:** `saturating_sub` hides over-release. `Warehouse::release` is public, so a caller can release units that belong to other holds, and nothing reports it.

**Concurrency**

- **Lock-order inversion, L245-247 vs L259-265:** `place_hold` takes `warehouse` then `holds`, and `confirm` takes `holds` then `warehouse`. `sweep_expired` (L272-273) also takes `warehouse` then `holds`. Thread A in `place_hold` holding `warehouse` and thread B in `confirm` holding `holds` will deadlock. Pick one global order (for example `warehouse` before `holds` everywhere) and restructure `confirm` to match.
- **`confirm`, L259 and L265:** `holds` is locked while `warehouse` is taken, which is part of the inversion above. The hold is also removed before the ship/release outcome is known, so a failure from `ship` drops the hold without restoring it.

**Minor**

- **Mutex poisoning:** every `lock().unwrap()` turns a panic in one thread into a panic in every later thread. Decide whether that is intended and document it.
- **`log`, L69 and L82-121:** the log grows without bound on a long-running service. Cap it or move it to an external sink.

ISSUES:
L47: available() underflows when reserved > on_hand (possible after record_loss)
L81: receive() overwrites existing SKU, resetting reserved and on_hand instead of adding
L120: record_loss() unchecked subtraction underflows and can break on_hand >= reserved
L127: total_value() u64 multiply and sum can overflow
L132: low_stock() inherits available() underflow
L157: deltas() indexes prices[i + 1] past end, panics on last iteration
L185: lookup() get_unchecked with untrusted slot is out-of-bounds read (UB)
L196: append_batch() reads through pointer invalidated by extend_from_slice realloc (UB)
L204: encode() truncates name length to u8 for names over 255 bytes, corrupting the record
L218: decode() from_utf8_unchecked on untrusted bytes is UB for invalid UTF-8
L245: place_hold() locks warehouse then holds, inverting order used in confirm (deadlock)
L259: confirm() locks holds then warehouse, inverting order used in place_hold/sweep (deadlock)
L253: place_hold() Instant + Duration panics on very large ttl
L265: confirm() removes hold before ship result is known; a failed ship loses the hold
L101: release() saturating_sub silently hides over-release of other holds' units