**Integer overflow / underflow panics**
- `reserve` L95: `reserved += qty` can overflow `u32` when stock is near `u32::MAX`.
- `ship` L112 & `record_loss` L120: `on_hand -= qty/lost` underflows if quantity exceeds current stock. Rust panics on underflow in debug builds, wraps in release.
- `total_value` L127: `u64 * u64` and `.sum()` can silently wrap or panic when high-value items accumulate.

**Out-of-bounds panic**
- `deltas` L156: Loop `0..prices.len()` reaches `i = len - 1`. Accessing `prices[i + 1]` reads past the slice end, panicking on the final iteration.

**Undefined behavior / memory safety**
- `append_batch` L194-196: `buf.as_ptr()` captures the current allocation. `extend_from_slice` may reallocate, moving the buffer. `first` becomes a dangling pointer; dereferencing it on L196 is use-after-free / UB.
- `decode` L218: `from_utf8_unchecked` assumes valid UTF-8. If the wire payload contains invalid bytes, the function triggers UB. The length check on L215 only validates bounds, not encoding.

**Concurrency / deadlock**
- `Service` L244 vs L258: `place_hold` locks `warehouse` then `holds`. `confirm` locks `holds` then `warehouse`. Opposite acquisition order creates a deadlock risk when threads interleave these paths. `sweep_expired` also locks `warehouse` -> `holds`, compounding the risk.

ISSUES:
L156: Out-of-bounds panic on final iteration
L95: Potential u32 overflow on `reserved += qty`
L112: Potential u32 underflow on `on_hand -= qty`
L120: Potential u32 underflow on `on_hand -= lost`
L127: Potential u64 overflow in `total_value`
L194: Pointer invalidation UB on reallocation in `append_batch`
L218: UB in `decode` with invalid UTF-8 wire data
L244/L258: Deadlock risk from inconsistent `warehouse`/`holds` lock ordering