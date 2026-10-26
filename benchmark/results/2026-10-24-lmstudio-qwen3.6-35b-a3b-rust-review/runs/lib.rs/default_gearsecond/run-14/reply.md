**Underflow & Panics**
- `available()` (L47) uses `-` without bounds checks. Debug panics; release wraps to huge values, breaking inventory math.
- `ship()` (L112) and `record_loss()` (L120) subtract from `on_hand` without verifying `qty`/`lost <= on_hand`. Same underflow risk.

**Overflow**
- `total_value()` (L127) multiplies `u32` and `u64` unchecked. `on_hand` (max ~4.3B) × `price_cents` (max ~1.8E19) exceeds `u64::MAX`, silently wrapping.

**Logic & Data Loss**
- `receive()` (L80) calls `insert()`, overwriting existing SKUs. Doc comment promises adding to `on_hand`.
- `encode()` (L204) casts `name.len()` to `u8`. Names > 255 bytes truncate silently, breaking round-trip decode.

**Out-of-Bounds & Undefined Behavior**
- `deltas()` (L157) accesses `prices[i + 1]` when `i` is the last index. Guaranteed panic on non-empty input.
- `lookup()` (L185) uses `get_unchecked()` on untrusted scanner input. Invalid index reads heap garbage; UB.
- `append_batch()` (L194) saves `buf.as_ptr()` before `extend_from_slice()`. Reallocation invalidates the pointer; dereferencing is UB.
- `decode()` (L218) uses `from_utf8_unchecked()` on unchecked bytes. Non-UTF-8 data is UB.

**Concurrency**
- `place_hold()` (L245) locks `warehouse` then `holds`. `confirm()` (L259) locks `holds` then `warehouse`. Inconsistent ordering causes deadlock under contention.

ISSUES:
L47: `available()` uses unchecked subtraction, panics or wraps on underflow
L80: `receive()` overwrites existing SKUs instead of adding to `on_hand`
L112: `ship()` subtracts from `on_hand` without bounds check, underflows
L120: `record_loss()` subtracts from `on_hand` without bounds check, underflows
L127: `total_value()` multiplies `u32` and `u64` unchecked, overflows `u64`
L157: `deltas()` accesses `prices[i + 1]` out of bounds, panics
L185: `lookup()` uses `get_unchecked()` on untrusted input, undefined behavior
L194: `append_batch()` saves pointer before `extend_from_slice()`, UB on reallocation
L204: `encode()` casts name length to `u8`, truncates names > 255 bytes
L218: `decode()` uses `from_utf8_unchecked()` on unchecked bytes, undefined behavior
L245/L259: Inconsistent lock ordering between `place_hold` and `confirm` causes deadlock