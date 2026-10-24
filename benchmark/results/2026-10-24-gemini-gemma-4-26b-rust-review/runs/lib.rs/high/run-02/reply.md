This review identifies several critical defects ranging from memory safety violations (Undefined Behavior) to concurrency deadlocks and logic errors.

### Memory Safety & Undefined Behavior (UB)
*   **Dangling Pointer in `append_batch` (L194-196):** The function calculates a pointer `first` using `buf.as_ptr()` after the initial `push`. However, it then calls `buf.extend_from_slice(tail)`. If this extension triggers a buffer reallocation, the pointer `first` becomes a dangling pointer to deallocated memory. Dereferencing it in the next line is a **Use-After-Free**.
*   **Unvalidated UTF-8 in `decode` (L218):** The function uses `std::str::from_utf8_unchecked` on bytes provided directly from the network buffer. If the input is not valid UTF-8, this invokes Undefined Behavior.
*   **Unsafe Bounds Check in `lookup` (L185):** The `lookup` method uses `get_unchecked` on a `slot` index provided by an external source (a handheld scanner). Because there is no bounds check, a malicious or malformed input will cause a memory safety violation.

### Concurrency Problems
*   **Deadlock in `Service` (L262/L265 vs L272/273):** There is an inconsistent lock acquisition order between `confirm` and `sweep_expired`.
    *   `confirm` acquires the `holds` lock first, then attempts to acquire the `warehouse` lock.
    *   `sweep_expired` acquires the `warehouse` lock first, then attempts to acquire the `holds` lock.
    If these two methods are called simultaneously on different threads, the service will deadlock.

### Logic Errors & Panics
*   **Overwrite instead of Increment in `receive` (L79):** The documentation states that for an existing SKU, units should be added to the current stock. However, `self.items.insert(sku, item)` replaces the existing entry entirely, losing the previous stock levels and metadata.
*   **Integer Underflow Panics:**
    *   **`deltas` (L157):** The loop iterates from `0..prices.len()`, but the body accesses `prices[i + 1]`. This will cause an out-of-bounds panic for any non-empty slice.
    *   **`available` (L47) & `record_loss` (L120):** `record_loss` can decrease `on_hand` without checking if it is greater than `reserved`. If `on_hand` becomes less than `reserved`, the `available()` method (and `low_stock` sorting) will panic due to integer underflow.
    *   **`ship` (L112):** While `ship` checks `qty > item.reserved`, it does not check `qty > item.on_hand`. If `on_hand` was previously reduced via `record_loss`, this will panic.

ISSUES:
L79: receive overwrites existing SKUs instead of adding to quantity
L47: available() panics on integer underflow if reserved > on_hand
L112: ship() can panic if on_hand < qty
L120: record_loss() can panic on integer underflow if lost > on_hand
L157: deltas() panics with out-of-bounds index access
L185: lookup() is UB if slot index is out of bounds
L194: append_batch() is UB due to use-after-free via pointer invalidation
L218: decode() is UB if input is not valid UTF-8
L262: confirm() and sweep_expired() deadlock due to inconsistent lock ordering