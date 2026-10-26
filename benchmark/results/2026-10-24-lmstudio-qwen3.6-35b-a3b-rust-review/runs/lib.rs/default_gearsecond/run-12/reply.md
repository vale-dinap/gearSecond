The code contains several critical defects across logic, safety, and concurrency.

**Logic Errors**
`receive` (L81) overwrites existing SKUs instead of adding stock, contradicting the doc comment. `encode` (L204) truncates the name length to `u8`, corrupting the wire format for long names. `place_hold` (L250) wraps `next_id` on overflow, causing ID collisions.

**Panics**
`available` (L47) and `record_loss` (L120) use checked subtraction without bounds checks, panicking if `reserved > on_hand` or `lost > on_hand`. `deltas` (L157) accesses `prices[i + 1]` unconditionally, panicking if `prices` is empty or has a single element.

**Undefined Behavior (UB)**
`lookup` (L185) uses `get_unchecked` on public input, allowing out-of-bounds reads. `append_batch` (L194) captures a raw pointer before `extend_from_slice`, which may reallocate the buffer, leaving the pointer dangling before reading it at L196.

**Integer Overflow**
`reserve` (L95) uses unchecked addition on `reserved`, panicking in debug or wrapping in release. `total_value` (L127) multiplies `on_hand` by `price_cents` without saturation, overflowing for high stock or price.

ISSUES:
L47: Underflow in `available` if `reserved > on_hand`.
L81: `receive` overwrites existing SKU instead of adding stock.
L95: Overflow in `reserved += qty`.
L120: Underflow in `on_hand -= lost`.
L127: Overflow in `total_value` calculation.
L157: Out-of-bounds panic in `deltas` loop.
L185: Undefined behavior in `lookup` via `get_unchecked`.
L194: Dangling pointer and UB in `append_batch` after reallocation.
L204: Name length truncation in `encode`.
L250: ID overflow in `place_hold`.