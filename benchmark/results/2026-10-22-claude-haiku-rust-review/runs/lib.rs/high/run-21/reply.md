I read the module without compiling or running it, so the repro cases below are reasoned from the code, not observed. Three findings are undefined behaviour and should block the merge.

## Undefined behaviour

- **L185, `SlotTable::lookup`:** `get_unchecked` runs on a slot index that comes from a scanner message. Out-of-range values read past the end of the allocation. The function is safe and public, so this is unsound, and "hot path" doesn't justify it. Use `self.slots.get(slot).copied().flatten()`.
- **L218, `decode`:** `from_utf8_unchecked` runs on network bytes. Invalid UTF-8 produces an invalid `String`, which is UB. Use `std::str::from_utf8(&rest[..len]).map_err(|_| InvError::Malformed("invalid utf-8"))?`.
- **L194–196, `append_batch`:** `first` is computed before `extend_from_slice`, which can reallocate the buffer. The dereference then reads freed memory. Repro: `let mut b = Vec::with_capacity(1); append_batch(&mut b, &[1, 2, 3]);`. The unsafe block isn't needed at all, because the first SKU is `head`.

## Deadlock

- **L245–247 and L272–273 vs. L259–265:** `place_hold` and `sweep_expired` lock `warehouse` then `holds`. `confirm` locks `holds` then `warehouse`. If one thread is in `confirm` holding `holds` while another is in `place_hold` holding `warehouse`, both wait forever. Pick one order everywhere. Taking `warehouse` first in `confirm` is the smallest change.

## Panics and overflow

Release builds wrap these silently, and debug builds panic.

- **L47, `available()`:** `on_hand - reserved` underflows once `reserved > on_hand`. That state is reachable: `receive(1,"x",5,0); reserve(1,5); record_loss(1,3);` leaves `on_hand = 2`, `reserved = 5`. In release, `available()` then becomes about 4 billion, so `reserve` accepts orders the shelf cannot fill.
- **L112 and L120:** `ship` and `record_loss` subtract without checking that the result stays non-negative. `record_loss` also never checks `reserved`, so it is what breaks the invariant above.
- **L127, `total_value`:** `on_hand as u64 * price_cents` and the `sum()` can both overflow for large prices or quantities. Use `checked_mul`/`checked_add`, or `u128`.
- **L156–157, `deltas`:** the loop runs `i` up to `len - 1` and then reads `prices[i + 1]`, which is `prices[len]`. Every non-empty input panics. Use `prices.windows(2)`. The subtraction can also overflow `i64`, so it needs `checked_sub` or a wider return type.
- **L253, `place_hold`:** `Instant::now() + ttl` panics for a large `Duration`, and the TTL comes from the caller. Use `checked_add` and return an error.

## Logic and data integrity

- **L81, `receive`:** `insert` replaces the whole entry. A restock resets `on_hand` to `qty`, zeroes `reserved` (orphaning outstanding holds), and overwrites name and price. This contradicts the doc comment, which says units are added. Use `entry().or_insert_with(...)` and add `qty` to `on_hand`.
- **L204, `encode`:** `name.len() as u8` silently truncates names over 255 bytes. The length byte then disagrees with the payload and the decoder reads the wrong fields. Reject long names with `Malformed`.
- **L101, `release`:** `saturating_sub` quietly clamps an over-release. That hides double-release bugs that `ship` would report. Return an error when `qty > reserved`.

## Lower severity

- **L82, `log`:** every receive, ship, and loss appends a `String` to an unbounded `Vec`. In a long-running service this is a memory leak. Cap it, use a ring buffer, or drop it in favour of real logging.

The existing tests cover none of this. Add a test that calls `deltas` on a non-empty slice, a test that does loss-then-reserve, and run `cargo miri test` on the unsafe paths.

ISSUES:
L47: available() underflows when reserved exceeds on_hand; wraps in release and oversells
L81: receive() replaces an existing SKU, resetting on_hand/reserved and contradicting its doc
L82: log Vec grows without bound in a long-running service
L101: release() saturates silently and masks over-release
L112: ship() on_hand subtraction can underflow after a loss
L120: record_loss() has no bounds check and can break reserved <= on_hand
L127: total_value() multiplication and sum can overflow
L157: deltas() indexes prices[len] and panics for every non-empty input
L185: lookup() uses get_unchecked on a scanner-supplied index (out-of-bounds read, UB)
L196: append_batch() dereferences a dangling pointer after a possible reallocation (UB)
L204: encode() truncates name length to u8, producing corrupt records
L218: decode() uses from_utf8_unchecked on untrusted bytes (UB)
L253: place_hold() panics on an overflowing ttl
L259: confirm() locks holds then warehouse, opposite to place_hold and sweep_expired (deadlock)