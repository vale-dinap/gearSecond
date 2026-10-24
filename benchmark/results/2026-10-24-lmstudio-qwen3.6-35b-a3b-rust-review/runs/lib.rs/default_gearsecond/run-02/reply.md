**Integer underflow in `Item::available` (L47)**
`self.on_hand - self.reserved` panics in debug or wraps in release if `reserved` ever exceeds `on_hand`. Should use `saturating_sub`.

**Unbounded subtraction in `Warehouse::ship` (L112)**
`item.on_hand -= qty` lacks a check against `on_hand`. If `qty > on_hand`, it underflows. `ship` only validates against `reserved`.

**Unbounded subtraction in `Warehouse::record_loss` (L120)**
`item.on_hand -= lost` can underflow if `lost > on_hand`. No validation or saturating arithmetic.

**Integer overflow in `Warehouse::total_value` (L127)**
`i.on_hand as u64 * i.price_cents` can overflow `u64` when both fields are large (max ~7.8e28). Use `checked_mul` or saturating arithmetic.

**Out-of-bounds panic in `deltas` (L156)**
Loop `0..prices.len()` iterates `len` times. On the final iteration `i = len - 1`, so `prices[i + 1]` accesses `prices[len]`, causing an index out of bounds panic.

**Undefined behavior in `SlotTable::lookup` (L185)**
`get_unchecked` skips bounds checking. Passing an out-of-range slot from a scanner causes UB. The comment claims it's a hot path, but safety must be preserved.

**Use-after-reallocation in `append_batch` (L194)**
`buf.as_ptr()` is captured before `extend_from_slice`. If `extend` reallocates the buffer, `first` points to freed memory. Dereferencing it at L196 is UB.

**Deadlock risk in `Service` (L245/L259/L272)**
`place_hold` locks `warehouse` then `holds`. `confirm` locks `holds` then `warehouse`. `sweep_expired` locks `warehouse` then `holds`. Inconsistent ordering across concurrent calls can deadlock.

ISSUES:
L47: `available` underflows if reserved exceeds on_hand
L112: `ship` underflows on_hand without bounds check
L120: `record_loss` underflows on_hand without bounds check
L127: `total_value` multiplication overflows u64
L156: Off-by-one loop bound causes out-of-bounds panic
L185: `get_unchecked` triggers UB on out-of-range slot
L194: Captured pointer invalidated by reallocation causes UB
L245/L259/L272: Inconsistent mutex lock ordering creates deadlock risk