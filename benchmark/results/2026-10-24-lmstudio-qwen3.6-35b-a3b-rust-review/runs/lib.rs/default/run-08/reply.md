Here is a review of the module focusing on real defects, categorized by impact.

### Logic & Invariant Violations
* **`Warehouse::receive` (L79-83)**: The documentation explicitly states that for an existing SKU, units should be added to the current stock. However, `self.items.insert(sku, item)` unconditionally overwrites the existing entry, silently discarding all prior `on_hand` and `reserved` values. This is a direct contradiction of the documented contract and a data-loss bug.
* **`Warehouse::record_loss` (L120)**: `item.on_hand -= lost;` will panic in debug builds or wrap silently in release builds if `lost > on_hand`. Inventory counts must never go negative. This should use `saturating_sub` or a checked subtraction with an appropriate error.
* **`Item::available` (L47)**: `self.on_hand - self.reserved` assumes the invariant `on_hand >= reserved` always holds. If that invariant is broken (e.g., via `record_loss` or a future code change), this subtraction underflows. It should defensively use `saturating_sub`.

### Panics & Out-of-Bounds Access
* **`deltas` (L156)**: `for i in 0..prices.len()` iterates up to `prices.len() - 1`. On the final iteration, `prices[i + 1]` accesses an out-of-bounds index, guaranteeing a panic for any non-empty input. The loop should be `0..prices.len().saturating_sub(1)` or `1..prices.len()`.

### Undefined Behavior & Memory Safety
* **`SlotTable::lookup` (L185)**: `get_unchecked` intentionally skips bounds checking. The comment claims this is a "hot path" optimization, but using it on an out-of-bounds `slot` is undefined behavior in Rust. The safe `self.slots.get(slot).copied()` should be used, or explicit bounds validation should precede the unsafe block.
* **`append_batch` (L194-197)**: `buf.as_ptr().wrapping_add(start)` captures a raw pointer *before* `buf.extend_from_slice(tail)`. If `extend_from_slice` triggers a reallocation, `first` becomes a dangling pointer. Dereferencing it with `unsafe { *first }` is a use-after-free and undefined behavior. This can be safely replaced with `buf[start]`.

### Codec & Protocol Defects
* **`encode` (L204)**: `name.len() as u8` truncates names longer than 255 bytes. Since the decoder expects a `u8` length prefix, this will cause silent data corruption or decode failures. The length prefix should be widened to `u16` or `u32`, or validated against the maximum supported size.
* **`decode` (L218)**: `std::str::from_utf8_unchecked` is undefined behavior if the slice is not valid UTF-8. The function only validates byte length, not character validity. It should use `std::str::from_utf8` to safely handle or reject invalid sequences.

### Concurrency Note
* **Lock Ordering Inconsistency**: `Service::confirm` locks `holds` then `warehouse`, while `sweep_expired` locks `warehouse` then `holds`. This inconsistent lock ordering can deadlock if both methods are called from the same thread (or in a reentrant context). Standardizing the lock acquisition order (e.g., always `warehouse` → `holds`) is necessary for correctness.

ISSUES:
L47: available() can underflow if reserved exceeds on_hand
L81: receive() unconditionally overwrites existing SKU data instead of adding to it
L120: record_loss() can underflow on_hand when lost exceeds current stock
L156: deltas() loop iterates one past the array bounds, causing a panic
L185: lookup() uses get_unchecked, which is UB on out-of-bounds slot indices
L194: append_batch() captures a raw pointer before extend_from_slice may reallocate, causing use-after-free
L204: encode() truncates name length to u8, breaking the codec for names > 255 bytes
L218: decode() uses from_utf8_unchecked without validating UTF-8, which is UB on invalid input