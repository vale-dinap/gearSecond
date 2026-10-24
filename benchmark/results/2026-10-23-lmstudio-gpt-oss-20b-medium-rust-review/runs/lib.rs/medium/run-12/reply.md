**Overview**

The module implements a tiny warehouse inventory system with an in‑memory `Warehouse`, a wire codec, a small statistics helper, and a thread‑safe front end (`Service`) that manages timed holds.  
Most of the logic is straightforward, but several functions contain real defects that can cause panics, undefined behaviour, integer overflows or data corruption.

Below is a line‑by‑line explanation of each problem, followed by a concise `ISSUES` list for quick reference.

---

### Detailed Problem Discussion

| Line | Function / struct | Issue | Why it matters |
|------|-------------------|-------|----------------|
| **46–48** (`Item::available`) | Subtracts `reserved` from `on_hand`. | If `reserved > on_hand` the subtraction underflows and panics. | The invariant is not enforced anywhere; e.g., after a failed `reserve`, `release`, or a manual mutation, this can happen. |
| **120** (`Warehouse::record_loss`) | Subtracts `lost` from `on_hand`. | No bounds check – an underflow panic if more items are lost than exist on hand. | Losses should be clamped to the current stock level. |
| **127** (`Warehouse::total_value`) | Multiplies `on_hand as u64 * price_cents`. | The product can overflow `u64` (e.g., a very large `price_cents` or many items). | Overflow silently wraps, giving an incorrect total value. |
| **155–158** (`deltas`) | Loops over `0..prices.len()` but accesses `i+1`. | On the last iteration `i+1 == prices.len()`, causing a panic (index out of bounds). | The function never returns and can crash callers. |
| **185** (`SlotTable::lookup`) | Uses `get_unchecked` without checking bounds. | Passing an out‑of‑range slot yields undefined behaviour. | Caller must validate the index; otherwise memory corruption or crashes occur. |
| **196** (`append_batch`) | Stores a pointer to the buffer before calling `extend_from_slice`. | The subsequent `extend_from_slice` may reallocate and move the data, making that pointer invalid. | Dereferencing it after reallocation is UB, potentially corrupting memory. |
| **204–205** (`encode`) | Casts `name.len()` to `u8`. | Names longer than 255 bytes are truncated or wrapped; information loss occurs silently. | The decoder will read an incorrect length and produce corrupted data. |
| **218** (`decode`) | Uses `from_utf8_unchecked` on the name slice. | If the slice contains invalid UTF‑8, a malformed string is produced without error. | Caller receives a possibly non‑UTF‑8 string; not UB but violates expectations of a “name”. |
| **245–251** & **259–266** (`Service::place_hold` / `confirm`) | Different lock acquisition order: `warehouse → holds → next_id` vs. `holds → warehouse`. | Two concurrent threads can deadlock – one holds the warehouse lock waiting for holds, while another holds the holds lock waiting for the warehouse. | The service becomes unresponsive under contention. |
| **(Additional)** `Service::sweep_expired` uses a mutable reference to `wh` inside the retain closure; this is legal but may be confusing and could hide subtle lifetime issues in future changes. |

---

### Summary of Real Defects

1. **Underflow in `Item::available`.**  
2. **Unbounded subtraction in `Warehouse::record_loss`.**  
3. **Potential u64 overflow in `Warehouse::total_value`.**  
4. **Out‑of‑bounds access in `deltas` (panic).**  
5. **Unsafe unchecked lookup in `SlotTable::lookup` (UB).**  
6. **Pointer invalidation after reallocation in `append_batch` (UB).**  
7. **Truncating name length to 8 bits in `encode`.**  
8. **Unchecked UTF‑8 conversion in `decode`.**  
9. **Deadlock risk due to inconsistent lock ordering in `Service`.**

---

### ISSUES

```
ISSUES:
L46: Item::available may underflow if reserved > on_hand.
L120: record_loss subtracts lost without bounds check, can panic.
L127: total_value multiplication can overflow u64 silently.
L156-158: deltas loops over all indices, accessing i+1 causes out‑of‑bounds panic.
L185: SlotTable::lookup uses unchecked get_unchecked → UB if slot out of range.
L196: append_batch dereferences pointer that may be invalid after extend → UB.
L204: encode truncates name length to u8, losing data for names >255 bytes.
L218: decode uses unsafe unchecked UTF‑8 conversion; may produce malformed string.
L245-L251 & L259-L266: inconsistent lock ordering in Service (warehouse→holds vs holds→warehouse) can deadlock under contention.
```

Please address these defects before merging.