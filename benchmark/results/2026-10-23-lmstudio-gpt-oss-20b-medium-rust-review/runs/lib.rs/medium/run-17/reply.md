The module contains several real‑world defects that can lead to panics, data corruption or undefined behaviour.  
Below is a brief description of each problem followed by the exact line numbers where they occur.

### 1. `Item::available` may underflow
```rust
pub fn available(&self) -> u32 {
    self.on_hand - self.reserved
}
```
If `reserved > on_hand`, subtraction wraps around to a very large number, breaking all logic that relies on this value (e.g., `reserve`, `ship`).  
**Line:** 46

### 2. `Warehouse::receive` overwrites existing SKUs
```rust
let item = Item { sku, name: name.to_string(), on_hand: qty, reserved: 0, price_cents };
self.items.insert(sku, item);
```
When the SKU already exists, this replaces the whole record instead of adding to `on_hand`, losing previous inventory and reservation data.  
**Lines:** 79‑81

### 3. `record_loss` can underflow
```rust
item.on_hand -= lost;
```
If `lost > on_hand`, the subtraction wraps around causing a huge positive number and corrupting the inventory.  
**Line:** 120

### 4. Off‑by‑one in `deltas`
```rust
for i in 0..prices.len() {
    out.push(prices[i + 1] - prices[i]);
}
```
The loop runs up to `len-1` but accesses `i+1`, which panics on the last iteration.  
**Lines:** 156‑158

### 5. Unsafe lookup in `SlotTable::lookup`
```rust
unsafe { *self.slots.get_unchecked(slot) }
```
If `slot` is out of bounds, this dereferences an invalid pointer → undefined behaviour. The function promises a safe return type (`Option<Sku>`) but the implementation violates safety guarantees.  
**Lines:** 184‑186

### 6. UB in `append_batch` due to potential reallocation
```rust
let first = buf.as_ptr().wrapping_add(start);
buf.extend_from_slice(tail);
let first_val = unsafe { *first };
```
The pointer `first` may become invalid if `extend_from_slice` reallocates the vector, leading to undefined behaviour when dereferenced.  
**Lines:** 191‑198

### 7. Truncation of name length in `encode`
```rust
out.push(name.len() as u8);
```
If a name exceeds 255 bytes, its length is truncated silently, producing an invalid wire format that cannot be decoded correctly.  
**Lines:** 204‑207

### 8. UB in `decode` due to unchecked UTF‑8 conversion
```rust
let name = unsafe { std::str::from_utf8_unchecked(&rest[..len]) }.to_string();
```
If the bytes are not valid UTF‑8, this violates Rust’s guarantees for `String`, resulting in undefined behaviour.  
**Line:** 219

### 9. Possible ID wrap‑around in `Service::place_hold`
```rust
let mut n = self.next_id.lock().unwrap();
*n += 1;
```
After `2^64-1` holds the counter will wrap to zero, producing duplicate IDs and breaking hold identification.  
**Lines:** 250‑253

### 10. Potential deadlock between `confirm` and `sweep_expired`
* `confirm`: locks `holds` → `warehouse`.  
* `sweep_expired`: locks `warehouse` → `holds`.  

If two threads acquire the first lock each, they can block forever waiting for the other’s lock, leading to a deadlock.  
**Lines:** 259‑266 (confirm) and 272‑274 (sweep_expired)

---

## ISSUES
```
L46: Item::available may underflow if reserved > on_hand.
L79-81: Warehouse::receive overwrites existing SKU instead of adding inventory.
L120: record_loss subtracts without checking for underflow, can wrap around.
L156-158: deltas loop accesses out‑of‑bounds index (i+1) causing panic.
L184-186: SlotTable::lookup uses unsafe get_unchecked; UB if slot is out of range.
L191-198: append_batch dereferences a pointer that may be invalid after reallocation → UB.
L204-207: encode truncates name length to u8, silently dropping data for names >255 bytes.
L219: decode uses from_utf8_unchecked, causing UB on non‑UTF8 input.
L250-253: next_id counter can wrap around, yielding duplicate hold IDs.
Deadlock risk: confirm locks holds then warehouse; sweep_expired locks warehouse then holds.```
