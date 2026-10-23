I found 13 defects: three cases of undefined behaviour, several panics on ordinary input, a deadlock, and a few logic errors that can leak stock or oversell. Line numbers refer to `src/lib.rs`.

## Undefined behaviour

**`lookup`, line 185.** `get_unchecked` takes an index straight from a scanner message. Any `slot >= len` reads past the end of the allocation. The "hot path" comment doesn't justify this: `get` costs almost nothing, and the index is untrusted, so the check has to stay. Use `self.slots.get(slot).copied().flatten()`.

**`append_batch`, lines 194 and 196.** `first` is a pointer taken before `extend_from_slice`, which can reallocate the buffer. Dereferencing `first` afterward reads freed memory whenever the buffer grows. The pointer isn't needed at all, since `head` already holds the value. Return `Some((head, buf.len()))`.

**`decode`, line 218.** `from_utf8_unchecked` runs on bytes from the network. Invalid UTF-8 produces a `String` that breaks its own invariant, which is UB. Use `std::str::from_utf8(...).map_err(|_| InvError::Malformed("bad utf-8"))?`.

## Panics

**`deltas`, line 157.** The loop runs `i` over `0..prices.len()` and reads `prices[i + 1]`. On the last iteration that index equals `len`, so any non-empty input panics. Use `prices.windows(2).map(|w| w[1] - w[0])`. The `i64` subtraction can also overflow for extreme values, so `checked_sub` is worth considering.

**`Item::available`, line 47.** `on_hand - reserved` underflows once `reserved > on_hand`. That state is reachable through `record_loss` (line 120). In debug builds it panics. In release builds it wraps to about 4.29 billion, so `reserve` accepts any quantity and oversells. The same underflow affects `low_stock` (line 133).

**`record_loss`, line 120.** The subtraction is unchecked. A loss larger than `on_hand` panics in debug and wraps in release. The function also never checks `reserved`, so it can break the `reserved <= on_hand` invariant that `ship` (line 112) relies on. Reject losses that exceed `on_hand - reserved`, or return an error.

**`place_hold`, line 253.** `Instant::now() + ttl` panics on overflow, for example with `Duration::MAX`. That happens after `reserve` at line 246 has already reserved the stock. The panic leaves the reservation with no hold to track it, and it poisons both mutexes. Use `checked_add` and return an error before reserving.

**Lock poisoning in general.** Every lock uses `.unwrap()`. Once any panic happens inside a locked section (lines 120, 127, 253), every later call on the service panics too. In a long-running server that turns one bad input into a full outage.

## Concurrency

**Lock-order inversion, lines 259 and 265 against 245/247 and 272/273.** `confirm` locks `holds` and then `warehouse`. `place_hold` and `sweep_expired` lock `warehouse` and then `holds`. If one thread is in `confirm` and another is in `place_hold`, each can end up waiting on the lock the other holds. Pick one order and use it everywhere.

## Logic errors

**`receive`, line 81.** `HashMap::insert` replaces the existing entry. The doc comment says units are added to what is on hand, but the code discards `on_hand` and resets `reserved` to 0. Any active holds for that SKU are then orphaned. Use `entry(sku)` and add `qty` to `on_hand` with `checked_add`.

**`confirm`, line 266.** The hold is removed at line 260, before `ship` runs. If `ship` returns `Insufficient`, which the `receive` bug above can cause, the hold is gone and its units stay in `reserved` forever. Call `ship` first and remove the hold only on success.

**`release`, line 101.** `saturating_sub` silently accepts a release larger than what is reserved. Callers can then make `available` exceed physical stock, which allows overselling. Return an error when `qty > reserved`.

**`encode`, line 204.** `name.len() as u8` truncates silently for names over 255 bytes. The length prefix then disagrees with the bytes that follow, and the decoder misreads the whole frame. Return an error instead, which means `encode` needs to return a `Result`.

## Overflow

**`total_value`, line 127.** `on_hand as u64 * price_cents` and the `sum` can overflow `u64`. This needs very large prices or counts, so the likelihood is low, but the fix is cheap: use `checked_mul`/`checked_add` or `u128`.

## Notes

- The existing tests cover none of these paths. Regression tests for the `deltas` off-by-one, the `receive` overwrite, and the `record_loss` underflow would be the most useful additions.
- I did not change any files; this was a read-only review.

ISSUES:
L47: `available()` underflows when `reserved > on_hand`; wraps in release and lets `reserve` oversell
L81: `receive()` overwrites an existing SKU, discarding `on_hand` and `reserved` despite the doc comment, and orphaning active holds
L101: `release()` silently saturates on over-release, inflating availability and enabling overselling
L120: `record_loss()` has an unchecked subtraction and can break the `reserved <= on_hand` invariant
L127: `total_value()` can overflow the `u64` multiplication and sum
L157: `deltas()` indexes `prices[len]` and panics on any non-empty input (off-by-one)
L185: `lookup()` uses `get_unchecked` on an untrusted index, causing an out-of-bounds read (UB)
L196: `append_batch()` dereferences a pointer that is dangling after `extend_from_slice` reallocates (UB)
L204: `encode()` truncates the name length with `as u8`, corrupting the frame for names over 255 bytes
L218: `decode()` uses `from_utf8_unchecked` on network data, which can create an invalid `String` (UB)
L253: `place_hold()` panics on `Instant + ttl` overflow after the stock is already reserved, leaking the reservation
L259: lock-order inversion between `confirm` (holds→warehouse) and `place_hold`/`sweep_expired` (warehouse→holds) can deadlock
L266: `confirm()` removes the hold before `ship`; a failed `ship` leaves the units reserved permanently