The module compiles, but several logical, safety, and concurrency defects exist that could cause panics, undefined behaviour, or incorrect inventory accounting in production use.

### Core problems

1. **`Warehouse::receive` replaces an existing SKU instead of adding to it** – the comment says “for an existing SKU the units are added …”, yet `HashMap::insert` overwrites the whole entry.  
2. **Under‑flow possible in several places**  
   * `Item::available`: `on_hand - reserved` can under‑flow if data corruption occurs or a previous bug leaves `reserved > on_hand`.  
   * `Warehouse::record_loss` and `Warehouse::ship` subtract from `on_hand` without bounds checks, so a loss that exceeds the current stock or an over‑shipped quantity will panic in debug builds.  
3. **`deltas` iterates one step too far** – it accesses `prices[i+1]` when `i == prices.len()-1`, causing a runtime panic.  
4. **Unsafe code with no safety guarantees**  
   * `SlotTable::lookup` uses `get_unchecked` without bounds checking; an out‑of‑range index results in UB.  
   * `append_batch` captures a raw pointer to the vector’s buffer before the slice is extended, so the pointer can become dangling if reallocation occurs.  
   * `decode` constructs a string from bytes with `from_utf8_unchecked`; invalid UTF‑8 data leads to UB instead of a recoverable error.  
5. **Potential deadlock in `Service`** – `place_hold` locks `warehouse` first, then `holds`, while `confirm` locks `holds` first and then `warehouse`. Two concurrent calls can therefore block each other indefinitely.  
6. **Overflow risk in value calculations** – `total_value` multiplies two 64‑bit numbers (`on_hand * price_cents`) which may overflow without warning.

---

## ISSUES:
```
L77: receive replaces existing SKU instead of adding quantity.
L46: available() subtracts without saturating; can underflow.
L112: ship subtracts from on_hand without bounds check, possible underflow.
L120: record_loss subtracts from on_hand; may underflow if lost > on_hand.
L156-158: deltas accesses prices[i+1] out of range.
L185: lookup uses unchecked index; UB if slot out of range.
L191-197: append_batch captures raw pointer before extend, can become dangling after reallocation.
L218-220: decode builds string with from_utf8_unchecked; invalid UTF‑8 causes UB.
L245/250: place_hold locks warehouse then holds; confirm locks holds then warehouse → potential deadlock.
```
