The module contains several real defects that can lead to panics, undefined behaviour, integer overflows or incorrect semantics.  
Below is a concise description of each problem followed by a numbered list of the offending lines.

### 1. `record_loss` may underflow `on_hand`
```rust
119 |         let item = self.items.get_mut(&sku).ok_or(InvError::UnknownSku(sku))?;
120 |         item.on_hand -= lost;          // <-- potential underflow
```
If `lost > on_hand`, the subtraction panics in debug builds and silently wraps in release builds, corrupting inventory data.

### 2. `total_value` can overflow `u64`
```rust
127 |         self.items.values().map(|i| i.on_hand as u64 * i.price_cents).sum()
```
The product of a `u32` (`on_hand`) and a `u64` (`price_cents`) may exceed `u64::MAX`, causing an overflow.

### 3. `deltas` reads past the end of the slice
```rust
156 |     for i in 0..prices.len() {
157 |         out.push(prices[i + 1] - prices[i]);   // <-- index out‑of‑bounds when i == len-1
```
The loop should run to `len-1` or iterate over adjacent pairs.

### 4. Unsafe pointer usage in `append_batch`
```rust
191 |     let (&head, tail) = batch.split_first()?;
192 |     let start = buf.len();
193 |     buf.push(head);
194 |     let first = buf.as_ptr().wrapping_add(start);   // pointer may be invalidated after extend
195 |     buf.extend_from_slice(tail);
196 |     let first_val = unsafe { *first };              // <-- UB: ptr can dangle
```
`buf.extend_from_slice` can reallocate, invalidating `first`. Dereferencing it is undefined behaviour.

### 5. Unsafe unchecked access in `SlotTable::lookup`
```rust
184 |         unsafe { *self.slots.get_unchecked(slot) }   // <-- UB if slot >= len
```
No bounds check is performed; an out‑of‑range index results in a crash or memory corruption.

---

## ISSUES:
L120: potential underflow when subtracting lost from on_hand  
L127: integer overflow possible in total_value calculation  
L157: array index out of bounds in deltas loop  
L194-196: unsafe pointer may dangle after extend_from_slice in append_batch  
L185: unchecked access to SlotTable.slots, UB if slot out of range