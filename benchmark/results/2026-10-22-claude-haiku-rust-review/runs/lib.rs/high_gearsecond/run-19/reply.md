The module has three undefined-behaviour sites, a panic that fires on every non-empty input to `deltas`, a lock-order deadlock, and a `receive` that breaks its own contract. The unsafe code should not merge as written.

## Memory safety and undefined behaviour

- **L185, `SlotTable::lookup`**: `get_unchecked` takes a slot from a scanner message, so an out-of-range slot is an out-of-bounds read. The "hot path" comment does not justify removing the check, since `get` is cheap. Use `self.slots.get(slot).copied().flatten()`.
- **L218, `decode`**: `from_utf8_unchecked` runs on network bytes. Invalid UTF-8 inside a `String` is immediate UB. Use `std::str::from_utf8(...)` and map the error to `Malformed`.
- **L194–197, `append_batch`**: `first` points into `buf`, but `extend_from_slice` can reallocate the buffer. `*first` then reads freed memory. The pointer is unnecessary because the first SKU is `head`. Return `Some((head, buf.len()))` with no `unsafe`.

## Panics and overflow

- **L157, `deltas`**: the loop runs `i` over `0..prices.len()` and reads `prices[i + 1]`. The last iteration indexes past the end, so any non-empty input panics. The subtraction can also overflow `i64`. Use `prices.windows(2).map(|w| w[1] - w[0])` and decide on `checked_sub` or a documented wrap.
- **L120, `record_loss`**: `on_hand -= lost` is unchecked. It panics in debug and wraps to about 4 billion units in release. It also ignores `reserved`, so `on_hand` can fall below `reserved`.
- **L47, `available`**: `on_hand - reserved` underflows once the `record_loss` bug above breaks `on_hand >= reserved`. `reserve` (L95), `ship` (L111–112) and `low_stock` all depend on that invariant.
- **L112, `ship`**: `on_hand -= qty` underflows for the same reason.
- **L127, `total_value`**: `on_hand as u64 * price_cents` and the `sum` can both overflow `u64`. Use `u128` or `checked_*` and return an error.
- **L253, `place_hold`**: `Instant::now() + ttl` panics for large `ttl` such as `Duration::MAX`. This happens after L246 has already reserved the stock, so the reservation leaks. Compute the expiry with `checked_add` before reserving.

## Logic errors

- **L79–81, `receive`**: the doc says units are added to an existing SKU, but the code replaces the whole `Item`. That overwrites `on_hand`, resets `reserved` to 0 while holds still exist, and overwrites name and price. Available stock is then overstated, which allows overselling. Use `entry(sku).and_modify(...).or_insert_with(...)`.
- **L203–204, `encode`**: `name.len() as u8` truncates names over 255 bytes. The length prefix then misframes the record, and `encode` returns no error. Reject long names and return a `Result`.
- **L101, `release`**: `saturating_sub` silently accepts over-release, which hides double-release bugs. Consider returning an error when `qty > reserved`.
- **L260–266, `confirm`**: the hold is removed before the fallible `ship`. If `ship` fails, the hold is gone and cannot be retried. Ship first and remove the hold on success.

## Concurrency

- **L265, `confirm` versus L245–247 and L273**: lock order is inverted. `place_hold` and `sweep_expired` take `warehouse` then `holds`. `confirm` holds `holds` and then takes `warehouse`. Two threads running `confirm` and `place_hold` can deadlock. Pick one order everywhere, or guard all state with one `Mutex`.
- **All `.lock().unwrap()` calls**: a panic while a lock is held poisons it, and every later call then panics. This is fine if intentional, but it is worth a comment.

## Lower severity

- **L82, L113, L121**: `log` grows without bound. In a long-running `Service`, every `confirm` appends a string forever.
- **L169, `SlotTable::new`**: `vec![None; n]` allocates `n` entries unchecked. This matters only if `n` can come from untrusted input.

## Checked and fine

- `moving_average`: empty and short inputs are handled, and the `u64` sum cannot overflow for realistic windows. The `assert!` on `window == 0` is a deliberate API panic.
- `decode` length check (L215) is correct. The `try_into().unwrap()` calls are on exact-length slices and cannot fail.
- `parse_command` and the existing tests are correct as written.

The tests cover only `reserve`/`ship`, the codec round trip and `parse_command`. Add tests for `deltas` (the panic would have shown up immediately), `append_batch`, hold expiry, `receive` on an existing SKU, and a two-thread `confirm`/`place_hold` case.

ISSUES:
L185: get_unchecked on untrusted slot index, out-of-bounds read (UB)
L218: from_utf8_unchecked on network bytes, invalid UTF-8 is UB
L196: append_batch reads through pointer invalidated by extend_from_slice reallocation (UB)
L157: deltas indexes prices[len], panics on any non-empty input
L157: deltas i64 subtraction can overflow
L120: record_loss underflows/wraps on_hand and ignores reserved
L47: available() underflows once on_hand < reserved
L112: ship on_hand -= qty underflows after record_loss breaks invariant
L127: total_value u64 multiply/sum overflow
L253: Instant + ttl panics after stock already reserved, leaks reservation
L81: receive overwrites item, loses on_hand, resets reserved, allows oversell
L204: encode truncates name length to u8, produces corrupt frame
L101: release saturating_sub hides over-release
L265: confirm locks holds then warehouse, opposite of place_hold/sweep, deadlock
L260: confirm removes hold before fallible ship, failure drops hold
L82: log grows unbounded in long-running service
L169: vec![None; n] unbounded allocation from caller-supplied n