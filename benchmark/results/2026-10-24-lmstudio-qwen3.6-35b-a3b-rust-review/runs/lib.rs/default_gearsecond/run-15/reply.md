### Logic & Arithmetic
`receive` replaces the entire `Item` entry on line 81, discarding previous `on_hand`/`reserved` counts. The doc comment claims it adds units; the code ignores existing state.

`available()` subtracts `reserved` from `on_hand` without bounds checking. If `reserved > on_hand` (possible after `record_loss` or `receive` bugs), it wraps to a huge number or panics in debug. `record_loss` has the same `on_hand -= lost` underflow risk.

`total_value` multiplies `on_hand as u64` by `price_cents` (u64). Both can be large; the product easily exceeds `u64::MAX`. Use `checked_mul` or saturating math.

### Panics & OOB
`deltas` loops `0..prices.len()` and accesses `prices[i + 1]`. When `i` reaches the last index, `i + 1` is out of bounds, causing a panic.

### Undefined Behaviour & Memory Safety
`SlotTable::lookup` calls `get_unchecked` on a scanner-supplied `slot`. If `slot >= slots.len()`, this reads past the `Vec`'s allocation. UB.

`append_batch` captures a raw pointer to `buf`'s head on line 194, then calls `extend_from_slice` on line 195. `extend_from_slice` may reallocate the buffer, invalidating the pointer. Dereferencing it on line 196 is UB.

`decode` passes untrusted network bytes to `from_utf8_unchecked`. If the slice isn't valid UTF-8, this is UB. `encode` casts `name.len()` to `u8`, truncating names >255 bytes and breaking round-trip decoding.

### Concurrency
`place_hold` locks `warehouse` then `holds`. `confirm` locks `holds` then `warehouse`. Concurrent calls can deadlock. `sweep_expired` locks `warehouse` then `holds`, compounding the ordering mismatch.

ISSUES:
L47: available() underflows if reserved > on_hand
L81: receive() overwrites existing SKU instead of adding qty
L120: record_loss() underflows on_hand
L127: total_value() overflows u64
L157: deltas() panics on OOB access
L185: lookup() uses get_unchecked on untrusted input -> UB
L195: append_batch() dereferences dangling pointer after reallocation -> UB
L204: encode() truncates name length to u8
L218: decode() uses from_utf8_unchecked on network data -> UB
L245: place_hold and confirm lock order mismatch causes deadlock risk