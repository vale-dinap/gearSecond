**Defects found**

* **Wrong inventory update logic** – `Warehouse::receive` replaces an existing SKU instead of adding to its current stock.  
* **Unprotected subtraction** – `record_loss`, `ship`, and the potential loss‑then‑reserve path can underflow `on_hand`.  
* **Unchecked multiplication** – `total_value` multiplies a 32‑bit quantity by a 64‑bit price, which may overflow a `u64`.  
* **Out‑of‑bounds access in `deltas`** – the loop iterates to the last index and then accesses `i+1`, causing a panic.  
* **Unsafe out‑of‑range read** – `SlotTable::lookup` uses `get_unchecked` without any bounds guard, leading to undefined behaviour if called with an invalid slot.  
* **Undefined behaviour in `append_batch`** – the pointer obtained before pushing is dereferenced after the vector may reallocate.  
* **Potential deadlock due to inconsistent mutex ordering** – `Service::place_hold`, `confirm`, and `sweep_expired` acquire `warehouse` and `holds` locks in different orders, which can deadlock when run concurrently.

---

### ISSUES:
L80: `receive` replaces an existing SKU instead of adding quantity.  
L120: `record_loss` subtracts from `on_hand` without bounds check – may underflow.  
L112: `ship` reduces `on_hand` after checking only `reserved`; if `on_hand < qty`, underflow occurs.  
L127: `total_value` multiplies u32 by u64, potentially overflowing u64.  
L156-157: `deltas` accesses `prices[i+1]` for i==len‑1 – out‑of‑bounds panic.  
L185: `SlotTable::lookup` uses unsafe unchecked indexing; UB if slot is out of range.  
L192-196: `append_batch` dereferences a pointer that may become invalid after Vec reallocation – UB.  
L245-L255: `place_hold` locks `warehouse` then `holds`; `confirm` does the reverse, enabling deadlock.  
L258-L267: `confirm` acquires `holds` before `warehouse`, conflicting with `place_hold`.  
L270-L273: `sweep_expired` also locks `warehouse` before `holds`, inconsistent ordering.