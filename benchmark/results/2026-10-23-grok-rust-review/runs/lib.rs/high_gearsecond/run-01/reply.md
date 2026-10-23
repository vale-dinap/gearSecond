The module has correctness bugs in stock accounting, several panic and overflow paths, three `unsafe` blocks that are undefined behavior on realistic inputs, and a lock-order deadlock in `Service`.

### Stock accounting

`receive` always `insert`s a brand-new `Item`. For an existing SKU that drops the previous `on_hand`, `reserved`, name, and price. The comment says a repeat receipt adds units. Any `Service` hold on that SKU is then pointing at a reservation that no longer exists.

`release` uses `saturating_sub` and returns `Ok` when `qty` is larger than `reserved`, so extra releases succeed and eat other reservations.

`record_loss` does `on_hand -= lost` with no check. In debug that panics when `lost > on_hand`; in release it wraps. A loss that is within `on_hand` but larger than unreserved stock leaves `reserved > on_hand`.

`available` is `on_hand - reserved`, so once that invariant breaks it panics in debug and wraps in release. `reserve` and `low_stock` both call it.

`ship` checks `qty` against `reserved` only, then does `on_hand -= qty`. If losses have already pulled `on_hand` below `reserved`, that subtraction panics or wraps.

`total_value` does `on_hand as u64 * price_cents` and then `sum()`. Either the multiply or the sum overflows `u64` (debug panic, release wrap), so the reported value is wrong for large prices or large catalogs.

### Panics in the helpers

`moving_average` `assert`s `window > 0`, so a zero window panics instead of returning an error.

`deltas` loops `i` over `0..prices.len()` and reads `prices[i + 1]`. Any non-empty slice panics on the last index. The intended length is `prices.len() - 1`, which the `with_capacity` call already uses. The subtraction is also plain `i64` arithmetic, so values such as `i64::MAX - i64::MIN` panic in debug and wrap in release.

### Undefined behavior

`SlotTable::lookup` calls `get_unchecked` on a slot taken from a scanner message. An out-of-range index is undefined behavior, not a bounds error.

`append_batch` takes `buf.as_ptr().wrapping_add(start)` and then `extend_from_slice`s the rest of the batch. Extension can reallocate and free that allocation. The later `unsafe { *first }` is a use-after-free. `head` is already a `Copy` value, so the pointer is unnecessary.

`decode` builds the name with `str::from_utf8_unchecked` on bytes from the network. Invalid UTF-8 is undefined behavior.

### Codec

`encode` stores `name.len() as u8`. A name longer than 255 bytes is written in full with a truncated length. `decode` then treats the wrong slice as the name and the following name bytes as `sku` and `qty`. If that cut splits a multibyte character, the unchecked UTF-8 read is also undefined behavior for output this encoder produced.

### `Service` concurrency and holds

`place_hold` and `sweep_expired` lock `warehouse` and then `holds`. `confirm` locks `holds` and then `warehouse`. One thread in `confirm` and another in `place_hold` or `sweep_expired` deadlock.

`place_hold` calls `reserve` before `Instant::now() + ttl`. `Instant + Duration` panics when the deadline does not fit. The panic unwinds after the reservation is committed and before the hold is inserted, so those units stay reserved with no hold id.

`confirm` `remove`s the hold before `release` or `ship`. If `ship` then returns `Insufficient` (reservations were cleared or over-released), the hold is gone and the remaining reservation cannot be confirmed or swept.

ISSUES:
L47: available computes on_hand - reserved and panics or wraps when reserved > on_hand
L81: receive overwrites an existing SKU, dropping on-hand quantity and reservations instead of adding qty
L101: release returns Ok and saturates when qty exceeds reserved
L112: ship subtracts qty from on_hand with no on_hand check, so it underflows when on_hand < qty
L120: record_loss subtracts lost from on_hand with no check and can leave reserved above on_hand
L127: total_value overflows u64 on the per-item multiply or on the sum
L144: moving_average panics when window is 0
L157: deltas reads prices[i + 1] for i in 0..len, so any non-empty slice panics
L157: deltas subtracts i64 prices with no overflow check
L185: lookup uses get_unchecked on an untrusted slot; an out-of-range index is undefined behavior
L196: append_batch dereferences a buf pointer after extend_from_slice may reallocate (use-after-free, undefined behavior)
L204: encode stores name.len() as u8, so names longer than 255 bytes produce a corrupt frame
L218: decode uses from_utf8_unchecked on network bytes; invalid UTF-8 is undefined behavior
L253: Instant::now() + ttl panics on overflow after reserve has already committed, leaking the reservation
L259: confirm locks holds then warehouse while place_hold and sweep_expired lock warehouse then holds, so they deadlock
L260: confirm removes the hold before release or ship; a later error leaves reserved units with no hold id