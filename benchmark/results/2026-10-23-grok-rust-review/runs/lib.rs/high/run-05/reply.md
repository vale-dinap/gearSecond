The module has merge-blocking defects in stock accounting, arithmetic, three `unsafe` blocks, the wire codec, and lock ordering.

### Inventory accounting

`receive` always `insert`s a brand-new `Item`. A second receipt of an existing SKU replaces `on_hand` with `qty` and zeroes `reserved`, and it also replaces the name and price. Anything already reserved is dropped while `Service` holds can still point at that SKU, so a later `confirm` ships against a reservation that no longer exists.

`release` uses `saturating_sub` and returns `Ok(())` when `qty` is larger than `reserved`. `reserve` and `ship` both report `Insufficient` for the same kind of mismatch, so an over-release silently destroys reservation state.

`record_loss` does `on_hand -= lost` with no check against `on_hand` or against unreserved units. In debug that panics when `lost > on_hand`. In release it wraps, and a smaller loss can leave `reserved > on_hand` (10 on hand, 8 reserved, lose 5 → 5 on hand, 8 reserved).

`available` is `on_hand - reserved`, so once that invariant is broken it panics in debug and wraps to a huge `u32` in release. `reserve` then trusts that wrapped “available” count. `ship` only checks `qty` against `reserved`, then does `on_hand -= qty`, which panics or wraps the same way.

### Overflow

`total_value` does `on_hand as u64 * price_cents` and then `sum()`s the products. A single expensive SKU overflows `u64` (panic in debug, wrap in release). One item with `on_hand` near `u32::MAX` and a large `price_cents` is enough.

`deltas` walks `0..prices.len()`. On every non-empty slice the last step reads `prices[i + 1]` one past the end and panics. The subtraction is also unchecked: `i64::MAX - i64::MIN` panics in debug and wraps in release. Signed overflow in Rust is defined, but the result is wrong. An empty slice happens to return an empty `Vec` because the range is empty.

`place_hold` computes `Instant::now() + ttl` after `reserve` has already succeeded. `Instant + Duration` panics when the deadline does not fit. That unwind poisons the warehouse and holds mutexes (both are held), leaves stock reserved with no hold row, and every later `lock().unwrap()` panics too.

### Undefined behaviour

`SlotTable::lookup` calls `get_unchecked` on a slot taken from a scanner message. An out-of-range index is UB, and it does not come back as `None`. `assign` bounds-checks, so this path is the unsound one.

`append_batch` takes `buf.as_ptr().wrapping_add(start)` and then `extend_from_slice`s the rest of the batch. `extend_from_slice` reallocates whenever capacity is short, which frees the buffer that pointer addresses. The following `*first` is a use-after-free. The value it wants is already in `head`.

`decode` is documented as a network parser and builds the name with `str::from_utf8_unchecked`. Non-UTF-8 bytes are UB. The later `try_into().unwrap()` calls on the `sku` and `qty` slices are safe: the length check makes those slices 4 bytes.

### Wire codec

`encode` stores `name.len() as u8`. A name of 256 bytes or more is truncated (256 becomes 0). The full name is still appended, so `decode` treats name bytes as the little-endian `sku` and `qty` and returns a successful, corrupted record whenever the buffer is long enough.

### Concurrency

The three mutexes are taken in conflicting orders:

- `place_hold` and `sweep_expired`: warehouse, then holds
- `confirm`: holds, then warehouse (on both the expired `release` path and the `ship` path)

One thread in `place_hold` or `sweep_expired` can hold the warehouse lock and wait for holds while `confirm` holds the holds lock and waits for the warehouse. That is a deadlock. `confirm` also `remove`s the hold before `release` or `ship` finishes. If `ship` returns an error, the id is gone, the units stay reserved, and neither `confirm` nor `sweep_expired` can repair it.

The existing tests cover a short ASCII round-trip, a happy-path ship, and one parse. They do not hit these paths.

ISSUES:
L47: available() underflows when reserved > on_hand (panic in debug, wrap in release)
L81: receive() inserts a new item over any existing SKU, replacing on_hand and clearing reserved
L101: release() saturates and returns Ok when qty > reserved, dropping reservation state
L112: ship() subtracts qty from on_hand after checking only reserved, so on_hand underflows when reserved > on_hand
L120: record_loss() does on_hand -= lost with no cap, panicking or wrapping and leaving reserved above on_hand
L127: total_value() multiplies and sums u64 stock values that overflow
L156: deltas() iterates through the last index and reads prices[i + 1] out of bounds
L157: deltas() subtracts i64 prices with no overflow check
L185: lookup() uses get_unchecked on an untrusted slot index (UB when out of range)
L196: append_batch() dereferences a pointer into buf after extend_from_slice can reallocate (use-after-free)
L204: encode() truncates name.len() to u8, so names longer than 255 bytes are framed as a different record
L218: decode() uses from_utf8_unchecked on network bytes (UB when they are not UTF-8)
L253: Instant::now() + ttl panics on overflow after reserve, poisoning the warehouse and holds mutexes
L259: confirm() locks holds then warehouse while place_hold and sweep_expired lock warehouse then holds (deadlock)
L260: confirm() removes the hold before release or ship commits, so failure leaks the reservation forever