I'll review the inventory module for logic errors, panics, overflow, and safety issues, and check the source so line numbers match.This module has merge-blocking bugs in stock accounting, several panic and overflow paths, three `unsafe` blocks that are undefined behaviour on realistic inputs, and a lock-order deadlock in `Service`.

### Stock accounting

`receive` always `insert`s a brand-new `Item`. For an existing SKU that drops the previous `on_hand`, `reserved`, name, and price, so a second receipt wipes reservations instead of adding units.

`available` is `on_hand - reserved`. That subtract underflows whenever `reserved > on_hand`: debug builds panic, release builds wrap to a huge "available" count. `reserve` then does `reserved += qty` against that wrapped value and can overflow too. `Item`'s fields are public, and `record_loss` creates this state on its own.

`record_loss` does `on_hand -= lost` with no check against `on_hand` or `available`. `lost > on_hand` panics in debug and wraps in release. A loss that only eats unreserved units still leaves `reserved > on_hand`.

`ship` checks `qty` against `reserved` only, then does `on_hand -= qty`. Once `reserved > on_hand`, a quantity that is reserved but no longer on the shelf underflows `on_hand`.

`release` uses `saturating_sub` and returns `Ok(())` when `qty` is larger than `reserved`. The reservation count shrinks by less than the caller asked, and outstanding holds no longer match `reserved`.

`total_value` multiplies `on_hand as u64 * price_cents` and sums the products. Either the multiply or the sum overflows `u64` (debug panic, release wrap), so the reported value is wrong for large stock or prices.

### Panics and overflow in the helpers

`deltas` walks `0..prices.len()` and reads `prices[i + 1]`. On every non-empty slice the last iteration indexes one past the end and panics. The `with_capacity(len - 1)` allocation shows the loop was meant to stop one short. Earlier pairs also compute `prices[i + 1] - prices[i]` with bare `i64` subtraction, which panics in debug and wraps in release when the difference does not fit (for example `i64::MAX - (-1)`).

`moving_average` `assert`s and aborts when `window == 0`. The window sum is a `u64`; a window whose counts exceed `u64::MAX` overflows that sum.

### Undefined behaviour

`SlotTable::lookup` calls `get_unchecked` on an index the comment says comes from a scanner message. Any `slot >= slots.len()` is undefined behaviour, not a normal bounds error.

`append_batch` takes `buf.as_ptr().wrapping_add(start)` and then `extend_from_slice`s the rest of the batch. Growth reallocates and frees that buffer; the following `*first` is a use-after-free. The value it tries to recover is `head`, which is already in hand. A batch larger than the spare capacity hits this immediately.

`decode` builds the name with `str::from_utf8_unchecked`. The buffer is network input. Invalid UTF-8 is undefined behaviour. `encode` makes that worse: `name.len() as u8` truncates, so a name longer than 255 bytes is written in full with a wrapped length. The decoder then cuts the name at the wrong byte, which can split a multibyte character and feed invalid UTF-8 into that `unchecked` call, and it reads `sku` and `qty` from the middle of the name.

### `Service` concurrency

Lock order is inverted:

- `place_hold` and `sweep_expired` lock `warehouse`, then `holds`.
- `confirm` locks `holds`, then `warehouse`.

One thread in `place_hold` or `sweep_expired` holding `warehouse` and waiting for `holds`, and another in `confirm` holding `holds` and waiting for `warehouse`, deadlock.

`confirm` `remove`s the hold before `release` or `ship` succeeds. If `ship` returns `Insufficient`, or `release` returns `UnknownSku`, the hold is already gone. Those units stay in `reserved` with no hold left to confirm or sweep.

`place_hold` calls `reserve` before it records the hold. `Instant::now() + ttl` panics when the deadline does not fit in `Instant` (a large `ttl`). `*n += 1` panics in debug at `u64::MAX` and wraps in release, so later holds reuse ids and `HashMap::insert` drops the previous `Hold`. In each of those cases the reservation is already committed and nothing rolls it back, so the units stay reserved indefinitely.

ISSUES:
L47: available() subtracts reserved from on_hand and panics or wraps when reserved is greater
L81: receive inserts a new Item and drops any existing on_hand and reserved for that SKU
L101: release saturates and returns Ok when qty is greater than reserved
L112: ship subtracts qty from on_hand after checking only reserved, so it underflows when reserved exceeds on_hand
L120: record_loss subtracts lost from on_hand with no bounds check and can leave reserved above on_hand
L127: total_value multiplies and sums u64 stock values and overflows
L144: moving_average asserts and panics when window is 0
L147: moving_average accumulates the window in u64 and overflows when the sum exceeds u64::MAX
L157: deltas reads prices[i + 1] through the last index and panics on every non-empty slice
L157: deltas subtracts i64 prices without an overflow check
L185: lookup uses get_unchecked on a scanner-supplied slot index and is undefined behaviour when the slot is out of range
L196: append_batch dereferences a pointer into buf after extend_from_slice can reallocate, which is a use-after-free
L204: encode stores the name length as u8, so names longer than 255 bytes get a truncated length prefix
L218: decode uses from_utf8_unchecked on network bytes, which is undefined behaviour for non-UTF-8 names
L250: next_id wraps or panics at u64::MAX, reusing hold ids and dropping the previous hold
L253: Instant::now() + ttl panics when the deadline overflows, after reserve has already committed
L259: confirm locks holds then warehouse while place_hold and sweep_expired lock warehouse then holds, so they deadlock
L260: confirm removes the hold before release or ship succeeds, so a failure leaves stock reserved with no hold