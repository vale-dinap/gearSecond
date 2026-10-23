I read the module but did not compile or run it, so the panic and overflow claims come from reading the code. The three undefined-behaviour items are the most urgent. Running `cargo +nightly miri test` would confirm them quickly, and a test calling `deltas(&[1, 2])` would confirm the panic.

## Undefined behaviour

**`SlotTable::lookup` (L183–186).** `get_unchecked` is called with a `slot` that comes from scanner input. Any out-of-range value is an out-of-bounds read. Because `lookup` is a safe `pub fn`, safe callers can trigger UB. The "hot path" comment does not justify this. `self.slots.get(slot).copied().flatten()` does the same job with a bounds check.

**`decode` (L218).** `from_utf8_unchecked` runs on bytes from the network. Invalid UTF-8 produces an invalid `str`, which is UB as soon as it is used. Use `String::from_utf8` and map the error to `InvError::Malformed`.

**`append_batch` (L194–196).** The pointer is taken at L194, then `extend_from_slice(tail)` at L195 can reallocate `buf`. The dereference at L196 then reads freed memory whenever the batch grows the buffer. The unsafe block is also unnecessary: `first_val` is always `head`. Return `Some((head, buf.len()))` and drop the pointer.

## Panics and integer problems

**`deltas` (L156–157).** The loop runs `i` up to `prices.len() - 1`, so `prices[i + 1]` reads one past the end on the last iteration. Every non-empty input panics. `prices.windows(2).map(|w| w[1] - w[0]).collect()` avoids this. The subtraction can also overflow `i64` for extreme prices, so use `checked_sub` if the inputs are untrusted.

**`Item::available` (L47).** `on_hand - reserved` underflows when `reserved > on_hand`. That panics in debug builds and wraps to about 4 billion in release builds. The wrapped value makes `reserve` (L91–92) accept any quantity. Section "Logic" below explains how that state is reached.

**`record_loss` (L120).** `on_hand -= lost` has no check and panics if `lost > on_hand`. It also ignores reservations. Losing reserved units leaves `on_hand < reserved`, which is the state that triggers the `available` underflow. Check against `available()` and return `Insufficient`, using `checked_sub`.

**`total_value` (L127).** `on_hand as u64 * price_cents` and the `.sum()` can both overflow `u64`. `price_cents` is already `u64`, so a large price times a large quantity can overflow, and summing across SKUs can overflow too. Use `checked_mul`/`checked_add`, or accumulate in `u128`.

**`place_hold` (L253).** `Instant::now() + ttl` panics when the result is not representable, for example with `Duration::MAX`. Use `checked_add` and return an error.

## Logic

**`Warehouse::receive` (L79–81).** The doc says receiving adds to existing stock, but `insert` replaces the whole `Item`. `on_hand` becomes `qty`, `reserved` becomes 0, and name and price are overwritten. Stock is lost (receiving 2 on top of 10 leaves 2). Reservations vanish while their holds still exist, so the warehouse can overcommit:

1. Hold A reserves 4 of 10.
2. `receive(sku, _, 2, _)` leaves `on_hand = 2`, `reserved = 0`.
3. `reserve(sku, 2)` succeeds, so `reserved = 2` while hold A still claims 4.
4. `confirm(A)` fails in `ship` (L108) with `Insufficient`, and the hold has already been removed (L260).

The fix is `entry(sku)` with `or_insert_with`, then `on_hand.checked_add(qty)`. Only set name and price on creation, or make the policy explicit.

**`Service::confirm` (L259–266).** The hold is removed before the shipment succeeds. If `ship` fails, the hold is gone and its reserved units stay reserved forever. Through the current `Service` methods I don't see how `ship` can fail, because `Service` never exposes `receive` or `record_loss`. Still, the order is fragile. Ship first and then remove the hold, or put it back on error.

**`Warehouse::release` (L101).** `saturating_sub` silently hides over-release, which usually means a double release or another accounting bug. Returning an error would surface it.

## Concurrency

**Lock-order inversion (L245–247, L259–265, L272–273).** `place_hold` takes the warehouse lock and then the holds lock. `sweep_expired` does the same. `confirm` takes the holds lock and then the warehouse lock, both on the normal path (L265) and the expired path (L262). If one thread is in `place_hold` holding the warehouse and waiting for holds, while another is in `confirm` holding holds and waiting for the warehouse, both hang. Pick one lock order everywhere, or put the warehouse and holds behind a single mutex. The `next_id` mutex could also be an `AtomicU64`.

## Wire format

**`encode` (L204).** `name.len() as u8` truncates names longer than 255 bytes, but the full name is still written. The length prefix and the payload disagree, so `decode` reads `sku` and `qty` from the wrong offset and returns garbage without an error. Reject or truncate names longer than 255 bytes, on a char boundary. Returning a `Result` is cleaner.

## Minor

- **`Warehouse.log` (L69, L82, L113, L121)** grows without bound in a long-running service. Cap it or drop it.
- **Test gaps.** Nothing covers receiving into an existing SKU, `deltas`, `record_loss`, invalid UTF-8, an out-of-range `lookup`, or concurrent use. A `deltas` test would have caught the panic at once.

## Checked and found fine

- `moving_average`: `window > len` yields an empty result, and the slice indices are in bounds.
- `decode` length arithmetic: `len` is a `u8`, so `len + 8` cannot overflow, and the slices are in bounds.
- `parse_command`: `u32` parsing rejects negative numbers.
- `snapshot`: the guard temporary does not outlive its borrow.

ISSUES:
L183: lookup uses get_unchecked on a scanner-supplied slot index, which is out-of-bounds UB reachable from safe code
L218: decode uses from_utf8_unchecked on network bytes, producing an invalid str (UB)
L196: append_batch dereferences a pointer that extend_from_slice may have invalidated by reallocating (use-after-free)
L156: deltas indexes prices[i + 1] past the end, so every non-empty input panics
L79: receive replaces the existing item instead of adding stock, dropping on-hand units, reservations, name and price
L120: record_loss subtracts without a check, panicking on underflow and possibly leaving on_hand below reserved
L47: available() underflows when reserved > on_hand, panicking in debug and wrapping to a huge value in release
L127: total_value overflows u64 in the multiply and in the sum
L253: Instant + ttl panics for large TTLs instead of returning an error
L259: confirm takes holds then warehouse, the reverse of place_hold and sweep_expired, so the two can deadlock
L260: confirm removes the hold before shipping, so a failed ship leaks its reserved units
L101: release uses saturating_sub, silently hiding over-release accounting bugs
L204: encode truncates the name length to u8 for names over 255 bytes, producing corrupt frames silently
L69: Warehouse.log grows without bound in a long-running service