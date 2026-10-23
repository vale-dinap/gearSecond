The most serious problems are undefined behaviour in `lookup`, `append_batch` and `decode`, plus a lock-order inversion that can deadlock `confirm`. `deltas` also panics on every non-empty input.

**Memory safety and undefined behaviour**

- **`lookup` (L185)** calls `get_unchecked` on a slot number that comes from a scanner message. Any slot at or past `slots.len()` is out-of-bounds UB. Use `self.slots.get(slot).copied().flatten()`.
- **`append_batch` (L194–196)** takes a raw pointer to the new element, then calls `extend_from_slice`, which can reallocate `buf`. The pointer then dangles and `*first` reads freed memory. The first SKU is just `head`, so return `head` and drop the pointer entirely.
- **`decode` (L218)** calls `from_utf8_unchecked` on bytes from the network. Invalid UTF-8 in a `String` is UB and breaks the type's invariants. Use `std::str::from_utf8` and map the error to `InvError::Malformed`.

**Panics and overflow**

- **`deltas` (L156–157)** loops `i in 0..prices.len()` and reads `prices[i + 1]`. For `i = len - 1` that is `prices[len]`, so any non-empty input panics. The `with_capacity(len - 1)` suggests the intended range is `0..len - 1`. The `i64` subtraction can also overflow for extreme values; use `checked_sub` or `saturating_sub`.
- **`available` (L47)** computes `on_hand - reserved`. Once `record_loss` lets `on_hand` drop below `reserved`, this underflows: a panic in debug builds and a wrapped value in release.
- **`record_loss` (L120)** does `on_hand -= lost` with no check against `on_hand` or `reserved`. Example: `on_hand = 5, reserved = 5`. `record_loss(3)` leaves `on_hand = 2, reserved = 5`. Then `ship(5)` passes the reservation check and panics at L112 on `on_hand -= qty`.
- **`ship` (L112)** has the same underflow once that invariant is broken.
- **`total_value` (L127)** multiplies `u64 * u64` and sums the results. Both can overflow.
- **`place_hold` (L253)** computes `Instant::now() + ttl`, which panics if the sum overflows. Use `checked_add` and return an error.
- **`encode` (L204)** does `name.len() as u8`. Names over 255 bytes silently truncate the length prefix, so the record is corrupt and will decode incorrectly.

**Concurrency**

- **Lock-order inversion (L262, L265 in `confirm`, against L245–247 in `place_hold`).** `place_hold` takes `warehouse` then `holds`. `confirm` holds `holds` (L259) and then takes `warehouse`. Two threads running these at once can deadlock. `sweep_expired` (warehouse then holds) matches `place_hold`, so `confirm` is the outlier. Pick one order everywhere, or restructure so only one lock is held at a time.

**Logic**

- **`receive` (L80–81)** does `HashMap::insert`, which replaces the existing item. The doc says the units should be added, but `on_hand` and `reserved` are reset to 0 while holds still point at that SKU. A later `confirm` then fails `ship` with `Insufficient`, after the hold has already been removed, so that stock is effectively lost. Merge into the existing entry instead.
- **Expired holds keep blocking stock (L89).** `reserve` does not account for expired holds. Stock stays unavailable until someone calls `sweep_expired`, and nothing in the module calls it automatically.
- **`release` (L101)** uses `saturating_sub`, which hides over-release bugs. Once `receive` can reset `reserved`, a mismatch here goes unnoticed.

The tests cover only the happy path. None of the cases above is exercised, and nothing covers the concurrent paths.

ISSUES:
L47: available() underflows when reserved > on_hand (panic in debug, wrap in release)
L80: receive() replaces an existing item, discarding on_hand/reserved while holds still reference it; doc says units should be added
L89: reserve() does not count expired holds; stock stays blocked until sweep_expired runs, which nothing calls automatically
L101: release() saturating_sub hides over-release mismatches
L112: ship() on_hand -= qty underflows once record_loss breaks on_hand >= reserved
L120: record_loss() has no bounds check; can underflow and leave on_hand below reserved
L127: total_value() u64 multiply and sum can overflow
L157: deltas() reads prices[len], panicking for any non-empty input; i64 subtraction can also overflow
L185: lookup() get_unchecked on scanner-supplied slot is out-of-bounds UB
L194: append_batch() pointer taken before extend_from_slice, which can reallocate; dangling read is UB
L204: encode() truncates names over 255 bytes with `as u8`, corrupting the record
L218: decode() from_utf8_unchecked on untrusted network bytes is UB on invalid UTF-8
L253: place_hold() Instant + ttl panics on overflow; use checked_add
L262: confirm() takes holds then warehouse, inverting place_hold's warehouse-then-holds order; deadlock risk