Here is the review of the inventory service module.

### Defects Analysis

**1. Integer Underflows and Panics**
- **`Item::available` (L47)**: The method computes `self.on_hand - self.reserved`. If `reserved` exceeds `on_hand` (which can happen if `record_loss` is called aggressively), this subtraction underflows. In debug builds, this panics; in release builds, it wraps around to a huge number, corrupting inventory logic.
- **`Warehouse::record_loss` (L120)**: Similarly, `item.on_hand -= lost` can underflow if `lost > on_hand`. This breaks the invariant that `on_hand >= reserved`, leading to downstream panics in `ship` or incorrect values in `available`.

**2. Integer Overflow**
- **`Warehouse::total_value` (L127)**: The expression `i.on_hand as u64 * i.price_cents` multiplies two `u64` values. Since `on_hand` is `u32` (max ~4.2 billion) and `price_cents` is `u64` (max ~1.8 × 10¹⁹), the product can easily exceed `u64::MAX`. This causes silent overflow or panic in debug mode.

**3. Out-of-Bounds Panic**
- **`deltas` (L157)**: The loop `for i in 0..prices.len()` iterates over all indices. Inside, it accesses `prices[i + 1]`. When `i` is the last index, `i + 1` equals `prices.len()`, causing an out-of-bounds panic. The loop bound should be `prices.len().saturating_sub(1)`.

**4. Undefined Behavior (UB)**
- **`SlotTable::lookup` (L185)**: `get_unchecked` skips bounds checks. If `slot` is out of range, this is UB. The comment mentions scanner input, which may be untrusted, making this unsafe.
- **`append_batch` (L196)**: `buf.as_ptr()` is captured before `extend_from_slice`. If `extend` causes a reallocation, the old pointer becomes dangling. Dereferencing it is UB. The value `head` is already available directly from `batch`.
- **`decode` (L218)**: `from_utf8_unchecked` assumes the input is valid UTF-8. For network data, this is unsafe; invalid UTF-8 triggers UB. `from_utf8` should be used instead.

**5. Concurrency / Deadlock**
- **`Service` Lock Ordering (L245 vs L259)**: `place_hold` locks `warehouse` then `holds`. `confirm` locks `holds` then `warehouse`. This inconsistent ordering creates a deadlock risk if threads call these methods concurrently.

**6. Data Loss**
- **`encode` (L204)**: `name.len() as u8` truncates names longer than 255 bytes. This violates the wire format or causes decode failures for valid items.

### ISSUES:
L47: `Item::available` underflows if `reserved > on_hand`
L120: `record_loss` underflows `on_hand` if `lost > on_hand`
L127: `total_value` multiplication can overflow `u64`
L157: `deltas` panics on out-of-bounds access `prices[i + 1]`
L185: `lookup` causes UB via `get_unchecked` on invalid input
L196: `append_batch` dereferences dangling pointer after potential reallocation
L218: `decode` causes UB via `from_utf8_unchecked` on untrusted data
L245: Deadlock risk due to inconsistent lock ordering in `place_hold` vs `confirm`
L204: `encode` truncates names longer than 255 bytes