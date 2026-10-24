**Overview of defects**

The module contains several real bugs that can lead to panics, incorrect behaviour, integer over‑flows or even undefined behaviour.  
Below is a detailed explanation of each defect followed by a concise list of line numbers where the problem occurs.

---

### 1. `Warehouse::receive` replaces an existing SKU instead of adding to it
```rust
pub fn receive(&mut self, sku: Sku, name: &str, qty: u32, price_cents: u64) {
    let item = Item { sku, name: name.to_string(), on_hand: qty, reserved: 0, price_cents };
    self.items.insert(sku, item);          // <‑ replaces any existing entry
}
```
* **Effect** – If the same SKU is received twice, the second call discards all previous inventory data (on‑hand, reserved and possibly a different name/price).  
* **Fix** – Merge with the existing `Item` or update its fields instead of inserting a new one.

---

### 2. Unsafely subtracting `reserved` from `on_hand` in `ship`
```rust
item.reserved -= qty;
item.on_hand -= qty;          // <‑ no check that on_hand >= qty
```
* **Effect** – If the inventory has been damaged or lost (`record_loss`) and `on_hand` is smaller than the quantity to ship, this underflows in debug mode (panic) and wraps around silently in release mode.  
* **Fix** – Add a guard: `if qty > item.on_hand { return Err(InvError::Insufficient{...}); }`

---

### 3. `Item::available` can underflow
```rust
pub fn available(&self) -> u32 {
    self.on_hand - self.reserved      // <‑ panics if reserved > on_hand
}
```
* **Effect** – After a buggy `receive`, or after `record_loss`, the invariant `reserved ≤ on_hand` may be violated, causing an underflow.  
* **Fix** – Use `saturating_sub` or return a checked value.

---

### 4. `Warehouse::record_loss` subtracts without bounds checking
```rust
item.on_hand -= lost;          // <‑ can underflow if lost > on_hand
```
* **Effect** – Damaging more items than exist results in an integer wrap‑around or panic.  
* **Fix** – Guard with `if lost > item.on_hand { return Err(...) }` or use `saturating_sub`.

---

### 5. Integer overflow in `total_value`
```rust
self.items.values().map(|i| i.on_hand as u64 * i.price_cents).sum()
```
* **Effect** – For large inventories or very expensive items the product can exceed `u64::MAX`, overflowing silently and producing an incorrect total value.  
* **Fix** – Compute using a larger type (`u128`) or check for overflow.

---

### 6. Off‑by‑one in `deltas`
```rust
for i in 0..prices.len() {
    out.push(prices[i + 1] - prices[i]);   // <‑ accesses out of bounds on the last iteration
}
```
* **Effect** – Panics when `prices` has at least two elements.  
* **Fix** – Iterate to `prices.len() - 1` or use `windows(2)`.

---

### 7. Unsafe read in `SlotTable::lookup`
```rust
unsafe { *self.slots.get_unchecked(slot) }
```
* **Effect** – If the caller passes an out‑of‑range slot, this dereferences invalid memory → undefined behaviour and possible crash.  
* **Fix** – Use a safe bounds check (`get`) or expose a safe API that guarantees the index is valid.

---

### 8. Unsafe pointer use in `append_batch`
```rust
let first = buf.as_ptr().wrapping_add(start);
buf.extend_from_slice(tail);            // may reallocate, invalidating `first`
let first_val = unsafe { *first };      // <‑ UB if reallocation happened
```
* **Effect** – After the `extend_from_slice`, the buffer can move in memory; the pointer stored in `first` becomes dangling, leading to a crash or data corruption.  
* **Fix** – Compute the first element after the extend or avoid raw pointers altogether.

---

### 9. Unsafe UTF‑8 conversion in `decode`
```rust
let name = unsafe { std::str::from_utf8_unchecked(&rest[..len]) }.to_string();
```
* **Effect** – If the byte slice is not valid UTF‑8, this results in undefined behaviour.  
* **Fix** – Use `std::str::from_utf8` and propagate an error on failure.

---

### 10. Truncation of name length in `encode`
```rust
out.push(name.len() as u8);          // <‑ truncates names longer than 255 bytes
```
* **Effect** – Long product names lose information; decoding will interpret the truncated length incorrectly.  
* **Fix** – Return an error or use a larger field type.

---

### 11. Potential deadlock in `Service` due to inconsistent lock ordering

| Method | Lock order |
|--------|------------|
| `place_hold` | warehouse → holds → next_id |
| `confirm`    | holds → warehouse |
| `sweep_expired` | warehouse → holds |

* **Effect** – A thread that calls `place_hold` can hold the warehouse lock while waiting for the holds lock, while another thread calling `confirm` holds the holds lock and waits for the warehouse lock. This circular wait is a classic deadlock scenario.  
* **Fix** – Adopt a single global order (e.g., always acquire `holds` before `warehouse`) or use separate mutexes per SKU.

---

### 12. Minor: `SlotTable::assign` overwrites without checking if the slot was already occupied
This isn’t a bug that causes undefined behaviour, but it may lead to accidental data loss if callers expect an error when re‑assigning a filled slot.

---

## ISSUES:
L81: `Warehouse::receive` replaces existing SKU instead of adding to it.  
L48: `Item::available` can underflow when reserved > on_hand.  
L120: `record_loss` subtracts lost without bounds checking, causing underflow.  
L112: `ship` subtracts from on_hand without ensuring enough stock, leading to underflow.  
L127: `total_value` may overflow u64 with large inventories or prices.  
L157-158: `deltas` accesses out of bounds (off‑by‑one).  
L185: Unsafe unchecked read in `SlotTable::lookup`, UB on invalid index.  
L194-196: Pointer from `buf.as_ptr()` can become dangling after reallocation in `append_batch`.  
L218: Unsafe UTF‑8 conversion in `decode`, UB if bytes are not valid UTF‑8.  
L204: Truncates name length to u8 in `encode`, losing data for names >255 bytes.  
L245-259: Inconsistent lock ordering between `place_hold` and `confirm`, leading to potential deadlock.