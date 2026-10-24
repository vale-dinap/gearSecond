I have reviewed the `src/lib.rs` module. Several critical defects ranging from memory safety violations to logic errors and potential panics were identified.

### Memory Safety and Undefined Behavior
*   **`SlotTable::lookup` (L185):** Uses `get_unchecked` on a `usize` index provided directly from external input (scanner message) without prior bounds checking. This is a classic out-of-bounds read vulnerability.
*   **`append_batch` (L194, L196):** Uses `wrapping_add` and raw pointer dereferencing to access `buf.as_ptr()`. If the `Vec` reallocates during `buf.extend_from_slice` (L195), the pointer `first` becomes dangling, leading to undefined behavior when dereferenced at L196.
*   **`decode` (L218):** Uses `from_utf8_unchecked` on a slice of bytes. While it checks length, it does not validate that the bytes are valid UTF-8, which can lead to undefined behavior if invalid sequences are processed as strings.

### Logic and Integrity Errors
*   **`Warehouse::receive` (L79-83):** The implementation uses `self.items.insert(sku, item)`. If the SKU already exists, it overwrites the entire `Item`, effectively deleting existing stock and reservation data instead of adding to `on_hand` as the documentation promises.
*   **`Warehouse::record_loss` (L120):** Subtracts `lost` from `on_hand` without checking if `lost > on_hand`. This will cause a panic in debug mode or a wrap-around in release mode.
*   **`Warehouse::ship` (L111-112):** While it checks if `qty > item.reserved`, it does not check if `qty > item.on_hand`. If `reserved` is somehow inconsistent with `on_hand`, this can panic or wrap.
*   **`Warehouse::total_value` (L127):** Multiplication of `u32` and `u64` can technically overflow if `on_hand` and `price_cents` are extremely large, though `u64` is likely sufficient for most inventory cases.

### Logic and Concurrency
*   **`deltas` (L157):** Iterates from `0..prices.len()`, but accesses `prices[i + 1]`. This will cause an out-of-bounds panic on the final iteration.
*   **`Service::confirm` (L262):** Acquires `self.warehouse.lock()` while already holding `self.holds.lock()`. While not a deadlock in this specific flow, the `sweep_expired` method (L272-273) acquires them in the same order, which is correct, but the logic inside `confirm` could lead to inconsistent states if an error occurs during the second lock acquisition.

ISSUES:
L47: Potential panic if `reserved > on_hand`
L79: `receive` overwrites existing items instead of adding to stock
L112: Potential underflow if `qty > on_hand`
L120: Potential underflow/panic if `lost > on_hand`
L147: Correct logic, but `moving_average` assumes `window <= daily.len()`
L157: Out-of-bounds panic on last element
L185: Out-of-bounds read via `get_unchecked` on unvalidated input
L194-196: Use-after-free/Undefined behavior due to pointer invalidation
L218: Undefined behavior via `from_utf8_unchecked` on unvalidated bytes