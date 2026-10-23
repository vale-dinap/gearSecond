I read the module without compiling or running it, so these findings come from reading the code. Line numbers refer to the listing. In debug builds, integer overflow panics; in release builds it wraps silently.

## Undefined behaviour (fix first)

**`lookup`, line 185.** `get_unchecked` is called on a slot index that comes from a scanner message. Any index at or past `slots.len()` is out of bounds, which is UB. Use `self.slots.get(slot).copied().flatten()`. The "hot path" comment doesn't justify skipping the check on untrusted input.

**`decode`, line 218.** `from_utf8_unchecked` runs on bytes received from the network. Invalid UTF-8 produces a `String` that violates its invariant, which is UB. Use `std::str::from_utf8(&rest[..len]).map_err(|_| InvError::Malformed("name not UTF-8"))?`.

**`append_batch`, lines 193–196.** `first` is computed before `buf.extend_from_slice(tail)`, and that call can reallocate `buf`. Dereferencing `first` afterwards reads freed memory. The dereference is also unnecessary, because the value is just `head`. Return `Some((head, buf.len()))` and remove the unsafe block.

## Concurrency

**Lock-order inversion, line 262.** `place_hold` (245, then 247) and `sweep_expired` (272, then 273) lock `warehouse` before `holds`. `confirm` locks `holds` (259) and then `warehouse` (262, 265). If one thread is in `place_hold` holding the warehouse lock while another is in `confirm` holding the holds lock, both block forever. Use one lock order everywhere.

**Leaked reservation and poisoned mutexes, line 253.** `wh.reserve` at 246 has already committed the units. `Instant::now() + ttl` panics on overflow for a large `ttl`, such as `Duration::MAX`. Because no hold records those units, they stay reserved forever. The panic also happens while the warehouse guard is held, which poisons the mutex, so every later `.unwrap()` panics too. Compute `expires` with `checked_add` and return an error before calling `reserve`.

## Logic and arithmetic

**`receive`, line 81.** `insert` replaces the whole item. The doc says units are added to existing stock, but this sets `on_hand = qty`, zeroes `reserved`, and overwrites the name and price. Live holds then refer to stock that no longer counts as reserved. Later, `sweep_expired` (278) or `ship` can release or consume reservations that belong to other holds, which can oversell. Use the `entry()` API and add to `on_hand`, with a checked add.

**`record_loss`, line 120.** Nothing checks that `lost` is within stock. `on_hand -= lost` underflows: it panics in debug and wraps to about 4 billion in release. It can also push `on_hand` below `reserved`, which breaks the invariant that `available()` depends on.

**`available`, line 47.** `on_hand - reserved` underflows once `reserved > on_hand`, which `record_loss` allows. `low_stock` (132) calls this for every item, so one bad SKU can panic the whole query. Fix the source in `record_loss`, and consider `saturating_sub` here as a backstop.

**`ship`, line 112.** `on_hand -= qty` can underflow for the same reason. Line 111 has already reduced `reserved` by then, so a debug panic leaves the item half-updated.

**`release`, line 101.** `saturating_sub` silently accepts releasing more than is reserved, which hides double releases and wrong quantities. Return `Insufficient`, as `ship` does.

**`confirm`, line 260.** The hold is removed before `ship` runs at 266. If `ship` fails, for example after the `receive` overwrite, the hold is gone and the caller can't retry. Check the stock first and remove the hold only after the ship succeeds.

**`encode`, line 204.** `name.len() as u8` truncates names longer than 255 bytes, but the full name is still written. The length prefix then disagrees with the payload, and `decode` reads the wrong fields. Use `u8::try_from(name.len())` and return an error.

**`total_value`, line 127.** `on_hand as u64 * price_cents` and the `sum()` can overflow `u64` with large prices. Use `checked_mul` and `checked_add`, or accumulate in `u128`.

**`deltas`, line 157.** `prices[i + 1] - prices[i]` can overflow `i64` for extreme inputs. Use `checked_sub` or `windows(2)`.

**`log`, line 69.** Every `receive`, `ship`, and `record_loss` appends a string and nothing ever trims the log. For a long-running service this grows without bound. Cap it, or drop it if nothing reads it.

## Checked and fine

- `moving_average` (146–147): the index arithmetic is in bounds. The `assert!` on `window == 0` is a deliberate precondition.
- `decode` length checks (215–220): these are correct, and the `try_into().unwrap()` calls can't fail after that check.
- `parse_command`: handles its cases correctly. It validates the verb last, which only changes the error message for bad input.
- `Service` is `Sync`. Its problems are deadlock and logic errors, not data races.

## Tests

The three existing tests cover none of the above. Add tests for: receiving into an existing SKU, `record_loss` beyond stock, non-UTF-8 and over-long names in the codec, out-of-range `lookup`, and `place_hold` with a very large TTL.

ISSUES:
L47: `available()` underflows when `reserved > on_hand`, which `record_loss` allows.
L69: `log` grows without bound in a long-running service.
L81: `receive` replaces existing SKUs, resetting `on_hand` and `reserved` instead of adding units.
L101: `release` saturates silently, hiding over-release.
L112: `ship` can underflow `on_hand` when `on_hand < reserved`.
L120: `record_loss` has no bounds check, so it underflows and can drop `on_hand` below `reserved`.
L127: `total_value` can overflow `u64` in the multiply or the sum.
L157: `deltas` can overflow `i64` in the subtraction.
L185: `lookup` uses `get_unchecked` on untrusted input, which is out-of-bounds UB.
L196: `append_batch` reads through a pointer that `extend_from_slice` may have invalidated.
L204: `encode` truncates the name length to `u8`, producing a corrupt record.
L218: `decode` uses `from_utf8_unchecked` on untrusted bytes, which is UB for invalid UTF-8.
L253: `Instant::now() + ttl` can panic after the reservation, leaking units and poisoning the mutexes.
L260: `confirm` removes the hold before `ship` can fail, losing it.
L262: `confirm` locks `holds` then `warehouse`, the reverse of `place_hold` and `sweep_expired`, which can deadlock.