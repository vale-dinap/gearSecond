The module can panic, wrap, deadlock, and hit undefined behavior on inputs the API accepts. Several of those paths also leave reserved units stuck with no hold.

**Stock invariant.** `available` does a raw `on_hand - reserved`. That panics in debug builds and wraps in release builds once `reserved` exceeds `on_hand`. `Item`'s fields are public, and two methods break the invariant themselves. `record_loss` subtracts `lost` from `on_hand` with no check, so a loss larger than `on_hand` panics or wraps, and a smaller loss can still push `on_hand` below `reserved`. After that, `ship` has already done `reserved -= qty` before `on_hand -= qty`, so an underflow panics with the reservation already reduced and nothing shipped. `release` uses `saturating_sub` and still returns `Ok`, so a too-large release clears every reservation on that SKU and those units can be reserved again while other holds are live.

`receive` does not add to an existing SKU. `insert` replaces the row, so a second receipt drops the previous `on_hand`, `reserved`, name, and price. Outstanding holds then no longer match the counter.

`total_value` does `on_hand as u64 * price_cents` and sums the products. Either the multiply or the sum overflows `u64` (debug panic, release wrap). For example, 4_000_000_000 units at 10_000_000_000 cents overflows the multiply.

**`deltas`.** The loop is `for i in 0..prices.len()` and then reads `prices[i + 1]`. Any non-empty slice panics on the last index: `[10, 12]` dies when `i == 1`. Pairs that do exist can also overflow `i64` (`i64::MAX - i64::MIN` and similar).

**Unsafe.** `SlotTable::lookup` is `get_unchecked` on a slot the comment says comes from a scanner. An out-of-range index is undefined behavior. `append_batch` takes `buf.as_ptr().wrapping_add(start)` and then `extend_from_slice`s the tail. That extend reallocates when the tail does not fit, the pointer dangles, and the later dereference is a use-after-free. The first SKU is already in `head`.

**Codec.** `encode` stores `name.len() as u8`, so a name longer than 255 bytes gets a truncated length but the full byte string is still written. `decode` trusts that length and builds the name with `from_utf8_unchecked`. Network bytes that are not UTF-8 are undefined behavior. A truncated prefix can also split a multibyte character, so a frame this encoder produced can trip that path.

**Holds and locking.** `place_hold` locks `warehouse`, then `holds`. `sweep_expired` uses that same order. `confirm` locks `holds`, then `warehouse`. One thread in `confirm` and another in `place_hold` or `sweep_expired` deadlock.

`place_hold` calls `reserve` before it builds the hold. `Instant::now() + ttl` panics when the deadline overflows (`Duration::MAX`, and any other TTL that does not fit). The panic runs while both mutexes are held, so both locks poison, the reservation stays, and no hold is inserted. `sweep_expired` will never see it.

`confirm` `remove`s the hold before `release` or `ship` finishes. If `ship` returns `Insufficient` or panics, the id is gone, the units stay reserved, and neither `confirm` nor `sweep_expired` can repair them.

`moving_average` and `parse_command` do not have the same class of bug. The `window > 0` assert is an explicit precondition.

ISSUES:
L47: available does unchecked on_hand - reserved (debug panic, release wrap)
L81: receive replaces an existing SKU instead of adding qty, wiping on_hand, reserved, name, and price
L101: release saturates and returns Ok when qty exceeds reserved, clearing other reservations on that SKU
L112: ship subtracts qty from on_hand with no check after reserved was already reduced (panic or wrap)
L120: record_loss subtracts lost from on_hand with no check and can leave reserved above on_hand
L127: total_value multiplies and sums in u64 with no overflow check (debug panic, release wrap)
L157: deltas reads prices[i + 1] for every i in 0..len and panics on any non-empty slice
L157: deltas subtraction can overflow i64
L185: lookup uses get_unchecked, so an out-of-range scanner slot is undefined behavior
L196: append_batch dereferences a pointer into buf after extend_from_slice can reallocate (use-after-free)
L204: encode casts name.len() to u8, so names longer than 255 bytes get a wrong length prefix
L218: decode uses from_utf8_unchecked on network bytes (undefined behavior on invalid UTF-8)
L253: Instant::now() + ttl panics on overflow after reserve, poisoning both mutexes and leaving no hold
L259: confirm locks holds then warehouse while place_hold and sweep_expired lock warehouse then holds (deadlock)
L260: confirm removes the hold before ship or release finishes, so failure strands reserved units forever