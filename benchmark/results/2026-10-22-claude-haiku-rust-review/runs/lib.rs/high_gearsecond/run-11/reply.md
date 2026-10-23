## Defects

**Undefined behaviour and memory safety**

- **L185 (`SlotTable::lookup`)**: `get_unchecked` takes a slot index from a scanner message without a bounds check. An out-of-range slot reads past the allocation, which is undefined behaviour. Use `self.slots.get(slot).copied().flatten()`.
- **L194-197 (`append_batch`)**: `first` is computed before `extend_from_slice(tail)`. That call can reallocate `buf`, leaving `first` dangling, so the read at L196 is a use-after-free. The first SKU is just `head`, so return it directly.
- **L218 (`decode`)**: `from_utf8_unchecked` runs on bytes from the network. Invalid UTF-8 is undefined behaviour. Use `std::str::from_utf8` and map the error to `Malformed`.

**Panics and arithmetic**

- **L156-157 (`deltas`)**: the loop runs `i` over `0..prices.len()`, so `prices[i + 1]` indexes past the end on the last iteration. Every non-empty input panics. Use `prices.windows(2).map(|w| w[1] - w[0])`.
- **L157**: the `i64` subtraction can overflow for extreme inputs. Use `checked_sub` or widen the arithmetic.
- **L47 (`Item::available`)**: `on_hand - reserved` underflows when `reserved > on_hand`. That state is reachable through `record_loss` (L120). In debug builds it panics. In release builds it wraps to a huge value, so `reserve` would accept far more than is on the shelf.
- **L112 (`ship`)**: `on_hand -= qty` relies on the invariant `reserved <= on_hand`, which `record_loss` can break.
- **L120 (`record_loss`)**: `on_hand -= lost` has no bounds check. It underflows when `lost > on_hand`, and it can also push `on_hand` below `reserved`.
- **L127 (`total_value`)**: `on_hand as u64 * price_cents` and the `sum()` can overflow `u64` with large prices. Use `checked_mul`/`checked_add` or `u128`.
- **L253 (`place_hold`)**: `Instant::now() + ttl` panics when `ttl` is very large. Use `checked_add` and return an error.

**Logic**

- **L80-81 (`receive`)**: `insert` replaces an existing SKU, resetting `on_hand` to `qty` and `reserved` to 0. The doc comment says units are added, and live holds lose their backing reservation.
- **L259-266 (`confirm`)**: the hold is removed at L260 before `ship` runs. If `ship` fails (L108-109), the hold is gone but its units stay in `reserved`, so that stock is locked permanently. Check first, or reinsert the hold on error.
- **L204 (`encode`)**: `name.len() as u8` silently truncates names longer than 255 bytes. The length prefix then disagrees with the payload and the frame is corrupt. Reject long names instead.

**Concurrency**

- **L245 vs L259**: `place_hold` locks `warehouse` then `holds`, while `confirm` locks `holds` then `warehouse`. Two threads running these concurrently can deadlock. `sweep_expired` (L272-273) uses the same order as `place_hold`, so that order should be the single rule.
- Every lock uses `.unwrap()`, so one panic while holding a lock poisons the mutex and takes down every later call. This is a design risk, not a bug in itself.

**Checked, no defect found:** `moving_average` (the range is empty when `window > len`, and the `u64` sum is safe), `release` (`saturating_sub`), and `parse_command`.

ISSUES:
L47: available() underflows when reserved > on_hand; wraps in release and allows overselling
L80: receive() overwrites an existing SKU, resetting on_hand and reserved instead of adding
L112: ship() subtracts from on_hand without checking on_hand >= qty
L120: record_loss() subtracts without bounds check; can underflow and drop on_hand below reserved
L127: total_value() multiplication and sum can overflow u64
L156: deltas() indexes prices[len] on the last iteration; panics on every non-empty input
L157: deltas() i64 subtraction can overflow for extreme values
L185: lookup() uses get_unchecked on an untrusted slot index; out-of-bounds read is UB
L194: append_batch() reads through a pointer invalidated by extend_from_slice reallocation; use-after-free
L204: encode() truncates name length to u8; corrupt frame for names over 255 bytes
L218: decode() uses from_utf8_unchecked on network bytes; invalid UTF-8 is UB
L253: place_hold() Instant + ttl panics on overflow for huge ttl
L259: confirm() locks holds then warehouse, opposite of place_hold() (L245); deadlock risk
L266: confirm() removes the hold before ship(); failed ship leaks the reservation permanently