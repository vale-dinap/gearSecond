This module has soundness holes in the unsafe codec and slot lookup, several debug-mode panics from unchecked arithmetic, and a lock-order deadlock in `Service`. The existing tests only cover the short happy path, so they miss all of this.

### Undefined behavior

`SlotTable::lookup` is a safe function and calls `get_unchecked`. A slot index from the scanner that is `>= slots.len()` is an out-of-bounds read. `SlotTable::new(0).lookup(0)` is undefined behavior. `assign` bounds-checks the same index.

`append_batch` saves `buf.as_ptr().wrapping_add(start)` and then calls `extend_from_slice`. That call mutably borrows the `Vec` and reallocates when `tail` does not fit in the spare capacity, which frees the buffer the pointer refers to. The later `*first` is a use-after-free. It is reachable whenever the vector is full after `push` and the batch has more than one SKU. The first SKU is already in `head`.

`decode` turns network bytes into a `&str` with `from_utf8_unchecked`. Invalid UTF-8 breaks the `str` invariant and is undefined behavior. A name longer than 255 bytes can hit this on a round trip: `encode` writes `name.len() as u8`, so the length prefix wraps, and the decoder can slice through the middle of a multibyte character.

### Panics and overflow

`deltas` iterates `0..prices.len()` and reads `prices[i + 1]`. Any non-empty slice panics on the last step. `deltas(&[1])` panics. Earlier pairs can also overflow `i64` (`i64::MAX - i64::MIN` panics in debug and wraps in release).

`Item::available` does `on_hand - reserved`. That underflows once `reserved > on_hand` (debug panic, release wrap). `low_stock` calls it while filtering and again while sorting. `record_loss` does `on_hand -= lost` with no comparison against `on_hand`, so `lost > on_hand` panics, and a smaller loss can still leave `reserved` above `on_hand`. `ship` only checks `qty <= reserved`, then does `on_hand -= qty`, so it underflows in that state. In debug the panic happens after `reserved` has already been reduced.

`total_value` computes `on_hand as u64 * price_cents` and then `sum()`. Either step panics in debug and wraps in release once the catalog is large enough. `moving_average(daily, 0)` hits `assert!` and panics. `next_id += 1` overflows after `2^64` holds: debug panic, or in release a wrapped id so `HashMap::insert` replaces a live hold and drops its reservation. `Instant::now() + ttl` panics when `ttl` does not fit in `Instant`. `place_hold` has already called `reserve` by then, so the units stay reserved and no hold is stored. A panic while a `Mutex` guard is alive poisons that mutex, and every later `lock().unwrap()` panics.

### Logic

`receive` is documented to add units to an existing SKU. It always `insert`s a brand-new `Item`, so the previous on-hand count, reservation, name, and price are discarded. A second receipt of a SKU that already has holds silently drops those reservations.

`release` uses `saturating_sub` and returns `Ok(())` when `qty` is larger than `reserved`. One oversized release clears every reservation on that SKU.

`encode` stores the name length in a `u8` and still appends the full byte string. For a name of 256 bytes or more the prefix wraps (`256` becomes `0`). `decode` then treats name bytes as the little-endian `sku` and `qty` and returns `Ok` with the wrong record.

`confirm` `remove`s the hold before `ship` returns. On `Insufficient` or on a panic inside `ship`, the id is gone and the reserved units have no hold left to confirm or sweep.

### Concurrency

Lock order is not consistent:

- `place_hold` and `sweep_expired` take `warehouse`, then `holds`.
- `confirm` takes `holds` and, still holding it, takes `warehouse` on both the expired path and the ship path.

One thread in `place_hold` or `sweep_expired` can hold `warehouse` and wait for `holds` while another thread in `confirm` holds `holds` and waits for `warehouse`. Both block forever, and the reserved stock stays stuck.

ISSUES:
L47: available() does on_hand - reserved with no check, so reserved > on_hand panics in debug and wraps in release; low_stock() calls the same path
L81: receive() inserts a new Item over an existing SKU, discarding on_hand and reserved instead of adding qty
L101: release() saturating_sub's and returns Ok when qty > reserved, clearing every reservation on that SKU
L112: ship() subtracts qty from on_hand after checking only reserved, so on_hand underflows when reserved > on_hand
L120: record_loss() does on_hand -= lost with no bounds check, underflows, and can leave reserved above on_hand
L127: total_value() multiplies and sums u64 with no overflow check (debug panic, release wrap)
L144: moving_average() asserts and panics when window is 0
L156: deltas() loops 0..len and reads prices[i + 1], panicking out of bounds on every non-empty slice
L157: prices[i + 1] - prices[i] overflows i64 (debug panic, release wrap)
L185: lookup() uses get_unchecked on an untrusted slot index, so slot >= len is undefined behavior
L196: append_batch() dereferences a pointer into buf after extend_from_slice(), which is use-after-free if the Vec reallocates
L204: encode() stores name.len() as u8, so names longer than 255 bytes are framed with a wrapped length and decode yields the wrong sku and qty
L218: decode() uses from_utf8_unchecked on network bytes, which is undefined behavior when the name is not valid UTF-8
L250: next_id += 1 overflows u64 (debug panic; release wrap makes insert overwrite a live hold and leak its reservation)
L253: Instant::now() + ttl panics when ttl overflows Instant, after reserve() and before the hold is inserted
L260: confirm() removes the hold before ship() finishes, so a failed ship leaks the reserved units and drops the id
L259: confirm() locks warehouse while still holding holds, inverting the warehouse-then-holds order of place_hold and sweep_expired, so concurrent calls deadlock