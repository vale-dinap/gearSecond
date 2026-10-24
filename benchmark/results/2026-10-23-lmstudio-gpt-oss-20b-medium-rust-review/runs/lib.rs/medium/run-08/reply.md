**Summary of defects**

1. **Logical overwrite on `receive`** – the method always inserts a new `Item`, discarding any existing data for that SKU instead of adding to the current stock.
2. **Unbounded subtraction in `record_loss`** – subtracting `lost` from `on_hand` can underflow and panic when the loss exceeds available units.
3. **Potential underflow in `Item::available`** – `self.on_hand - self.reserved` panics if `reserved > on_hand`, which can happen after a loss that brings `on_hand` below the reserved amount.
4. **Out‑of‑bounds indexing in `deltas`** – iterating from `0..prices.len()` and accessing `i+1` causes a panic when `i == prices.len() - 1`.
5. **Unsafe unchecked access in `SlotTable::lookup`** – the public API can be called with an out‑of‑range index, leading to undefined behaviour.
6. **Undefined behaviour after possible reallocation in `append_batch`** – the pointer stored in `first` may become invalid once `extend_from_slice` reallocates the buffer; dereferencing it is UB.
7. **Name length truncation in `encode`** – casting a name longer than 255 bytes to `u8` silently discards high bits, corrupting the wire format.
8. **Unsafe UTF‑8 conversion in `decode`** – using `from_utf8_unchecked` accepts any byte sequence; malformed data triggers UB.
9. **Deadlock risk in `Service`** – `place_hold` locks `warehouse` then `holds`, while `confirm` and `sweep_expired` lock them in the opposite order, allowing a classic deadlock if two threads interleave these calls.
10. **Possible overflow in `total_value`** – multiplying `on_hand` (u64) by `price_cents` can exceed 2⁶⁴, silently wrapping.

---

### ISSUES:
```
L80: receive() always inserts a new Item, discarding existing SKU data
L47: available() subtracts on_hand - reserved without checking, may underflow
L120: record_loss() subtracts lost from on_hand, can underflow and panic
L156: deltas() iterates 0..prices.len(), accessing i+1 causes out‑of‑bounds
L185: SlotTable::lookup uses unsafe get_unchecked; out‑of‑range index is UB
L192: append_batch may dereference a stale pointer after extend_from_slice reallocates
L204: encode truncates name length >255 bytes by casting to u8, corrupting format
L218: decode uses from_utf8_unchecked, accepting invalid UTF‑8 and causing UB
L245-259: Service place_hold locks warehouse then holds; confirm locks them in reverse, risking deadlock
L127: total_value multiplies two u64s; overflow silently wraps
```