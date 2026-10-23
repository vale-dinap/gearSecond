The module has four serious problems: an out-of-bounds read and a dangling-pointer dereference (both UB), an unchecked UTF-8 conversion on network input (also UB), and a lock-order deadlock. Several inventory invariants can also be broken, which leads to panics in debug builds and silent wraparound in release builds. I reviewed by reading only; I did not compile or run anything.

**Undefined behaviour and memory safety**

- **`lookup`, L185.** `get_unchecked` takes a slot from a scanner message, so an out-of-range value reads past the end of the `Vec`. The "hot path" comment doesn't justify it. Use `self.slots.get(slot).copied().flatten()`.
- **`append_batch`, L194–197.** `first` is computed before `extend_from_slice`, which can reallocate `buf`. The read at L196 then dereferences a dangling pointer. The result is always `head` anyway, so the `unsafe` block can go.
- **`decode`, L218.** `from_utf8_unchecked` runs on bytes from the network. Invalid UTF-8 is UB and can break `String` invariants later. Use `std::str::from_utf8` and map the error to `Malformed`.

**Concurrency**

- **Deadlock, L259/262/265 vs L245/247 and L272/273.** `confirm` locks `holds` then `warehouse`. `place_hold` and `sweep_expired` lock `warehouse` then `holds`. If one thread is in `confirm` while another is in `place_hold` or `sweep_expired`, each can hold one lock and wait for the other. Pick one order (warehouse, then holds) and use it everywhere.
- **Reservation leak, L260 and L266.** The hold is removed before `ship` runs. If `ship` fails, the hold is gone but its units stay reserved forever. Ship first and remove the hold only on success.

**Logic and invariants**

- **`receive`, L80–81.** The doc at L77–78 says units are added to an existing SKU. The code replaces the item, which resets `reserved` to 0 while holds may still be outstanding. Later `ship` calls then underflow.
- **`record_loss`, L120.** No check that `lost <= on_hand` or that `on_hand >= reserved`. Either can break the invariant.
- **`available`, L47, and `ship`, L112.** Once `reserved > on_hand`, `available` underflows. Debug builds panic. Release builds wrap to a huge value, so `reserve` will allow overselling.
- **`encode`, L204.** `name.len() as u8` truncates names over 255 bytes. The length prefix then disagrees with the payload and the frame is corrupt. Reject long names.
- **`total_value`, L127.** `on_hand as u64 * price_cents` and the `sum()` are unchecked. Use `checked_mul`/`checked_add`, or `u128`.
- **`deltas`, L157.** `prices[i+1] - prices[i]` overflows `i64` for extreme inputs.

`moving_average` (asserting on `window == 0`), `parse_command`, and `SlotTable::assign` look correct to me. The tests don't cover any of the issues above. A test for `record_loss` past `on_hand`, a receive-then-ship sequence, and an over-length name would catch most of them.

ISSUES:
L47: available() underflows when reserved > on_hand; wraps in release and allows overselling
L80: receive() replaces existing SKU, zeroing reserved; doc says units should be added
L112: ship() on_hand -= qty underflows when on_hand < reserved
L120: record_loss() has no bounds check; can underflow and break on_hand >= reserved
L127: total_value() unchecked u64 multiply and sum; overflows for large stock x price
L157: deltas() i64 subtraction overflows for extreme prices
L185: lookup() get_unchecked with scanner-supplied slot; out-of-bounds read (UB)
L196: append_batch() dangling pointer after extend_from_slice may reallocate (UB)
L204: encode() truncates names over 255 bytes with `as u8`; corrupt frame
L218: decode() from_utf8_unchecked on untrusted bytes; UB on invalid UTF-8
L259: confirm() locks holds then warehouse; opposite order to place_hold/sweep_expired; deadlock
L264: confirm() removes hold before ship; failed ship leaks the reservation