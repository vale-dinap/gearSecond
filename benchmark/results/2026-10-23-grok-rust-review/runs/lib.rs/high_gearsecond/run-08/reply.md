I'll review the module for logic bugs, panics, overflow, undefined behavior, and concurrency issues.The module corrupts stock counts, panics on ordinary inputs, has three undefined-behavior holes, and can deadlock in `Service`.

### Inventory accounting

`available` does a raw `on_hand - reserved`. Any state where `reserved` exceeds `on_hand` panics in debug builds and wraps in release builds. `low_stock` calls this twice, so it hits the same fault.

`receive` always `insert`s a brand-new `Item`. For an SKU that is already present, the previous `on_hand` and `reserved` are discarded and replaced by the new `qty` with `reserved: 0`. A second receipt of an existing SKU shrinks stock and drops outstanding reservations, so later `ship` calls no longer match the holds.

`release` uses `saturating_sub` and returns `Ok(())` when `qty` is larger than `reserved`. The reservation count collapses to zero, including units reserved for other callers.

`record_loss` does `on_hand -= lost` with no check. `lost > on_hand` panics in debug and wraps in release (stock becomes huge). A smaller loss that still eats into reserved units leaves `reserved > on_hand`, which is the state that breaks `available` and `ship`.

`ship` checks `qty` only against `reserved`, then decrements `reserved` before `on_hand`. When `on_hand < qty`, the `on_hand` subtraction panics or wraps after `reserved` has already changed.

`total_value` multiplies `on_hand as u64 * price_cents` and sums the products in `u64`. Either step overflows: debug panic, release wrap.

### `deltas`

```rust
for i in 0..prices.len() {
    out.push(prices[i + 1] - prices[i]);
}
```

On every non-empty slice the last `i` is `len - 1`, so `prices[i + 1]` panics. For two or more prices, earlier iterations run first and `i64` subtraction can overflow (`i64::MAX - (-1)`, `i64::MIN - 1`): panic in debug, wrap in release. An empty slice returns an empty vec and is fine.

### Undefined behavior

`SlotTable::lookup` calls `get_unchecked` on a slot the comment says comes from a scanner. `slot >= slots.len()` is undefined behavior.

`append_batch` stores `buf.as_ptr().wrapping_add(start)`, then calls `extend_from_slice`, then dereferences that pointer. The `&mut` use invalidates it, and any reallocation frees the buffer. The read is a use-after-free. `head` already holds that SKU.

`decode` builds a `String` with `from_utf8_unchecked` on bytes it describes as a network record. Invalid UTF-8 is undefined behavior. The length check only prevents a short buffer; it does not validate UTF-8.

### Codec

`encode` stores `name.len() as u8`. Lengths above 255 truncate (300 becomes 44, 256 becomes 0). `decode` then treats the front of the name as the whole name and reads the SKU and quantity from the wrong offset, returning `Ok` with corrupted fields. If that truncated prefix splits a multibyte character, the unchecked UTF-8 read in `decode` is undefined behavior on `encode`'s own output.

### `Service` concurrency and holds

Lock order is inverted:

- `place_hold` and `sweep_expired` take `warehouse`, then `holds`.
- `confirm` takes `holds`, then `warehouse` (both the expiry `release` and the `ship` path).

One thread in `place_hold` or `sweep_expired` holding `warehouse` and waiting for `holds`, and another in `confirm` holding `holds` and waiting for `warehouse`, deadlock.

`place_hold` calls `reserve` before `Instant::now() + ttl`. That addition panics when `ttl` does not fit in `Instant` (`Duration::MAX` and other large values). The panic happens after the stock is reserved and before the hold is inserted, so nothing will ever `release` or `sweep` those units. Unwind also poisons the `warehouse` and `holds` mutexes; later `lock().unwrap()` calls panic.

ISSUES:
L47: available() subtracts reserved from on_hand unchecked, so reserved > on_hand panics in debug and wraps in release
L81: receive() overwrites an existing SKU, discarding current on_hand and reserved and keeping only the new qty
L101: release() saturates and returns Ok when qty exceeds reserved, clearing reservations it should reject
L112: ship() decrements on_hand with no on_hand check after reserved is already reduced, panicking or wrapping when on_hand < qty
L120: record_loss() subtracts lost from on_hand with no check, panicking, wrapping, or leaving reserved above on_hand
L127: total_value() overflows u64 on the per-item multiply or the sum (debug panic, release wrap)
L156: deltas() loops 0..len and reads prices[i + 1], panicking on every non-empty slice
L157: deltas() subtracts i64 values with no overflow check (debug panic, release wrap) on earlier pairs
L185: lookup() uses get_unchecked on scanner input, so an out-of-range slot is undefined behavior
L196: append_batch() dereferences a Vec pointer after extend_from_slice has invalidated it (use-after-free, undefined behavior)
L204: encode() truncates name.len() to u8, so names longer than 255 bytes decode as corrupted sku/qty
L218: decode() uses from_utf8_unchecked on network bytes, so invalid UTF-8 is undefined behavior
L253: Instant::now() + ttl panics on overflow after reserve(), leaking that reservation and poisoning the mutexes
L259: confirm() locks holds then warehouse while place_hold() and sweep_expired() lock warehouse then holds, so they deadlock