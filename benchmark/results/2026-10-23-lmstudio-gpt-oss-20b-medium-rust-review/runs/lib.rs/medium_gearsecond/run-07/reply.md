The module contains several subtle defects that can lead to panics, incorrect
behaviour or undefined behaviour.  
Below is a short walk‑through of the most important problems followed by an
`ISSUES:` section that lists each defect together with its line number.

### Quick rundown

1. **`Warehouse::receive`** replaces an existing SKU instead of adding to the
   current stock, violating the documented semantics.
2. **`record_loss`** subtracts from `on_hand` without bounds checking,
   causing a wrap‑around underflow when the loss exceeds available stock.
3. **`total_value`** multiplies two 64‑bit values and sums into a 64‑bit
   accumulator; overflow silently wraps, giving an incorrect total for large
   inventories.
4. **`deltas`** iterates `0..prices.len()` but accesses `prices[i+1]`,
   which panics on the last iteration.
5. **`SlotTable::lookup`** dereferences a raw pointer obtained via
   `get_unchecked`; if the slot index is out of bounds this results in UB.
6. **`append_batch`** takes a raw pointer to the buffer before any mutation,
   then mutates the vector (`push`, `extend`). The pointer can become dangling,
   leading to undefined behaviour when it’s dereferenced later.
7. **`Service::place_hold` vs. `confirm/sweep_expired`** lock ordering is
   inconsistent: one path locks `warehouse` first, then `holds`; another path
   does the reverse. This can deadlock under concurrent use.

---

## ISSUES:

```
L80: receive replaces existing SKU instead of adding to on_hand
L120: record_loss may underflow on_hand when lost > current stock
L127: total_value overflows u64 silently for large inventories
L156: deltas panics on last element due to out‑of‑range index access
L185: lookup uses unsafe get_unchecked, UB if slot out of range
L194-196: append_batch keeps a raw pointer after possible reallocation → UB
L245: place_hold locks warehouse before holds; confirm/sweep_expired lock order reversed → deadlock risk
```
