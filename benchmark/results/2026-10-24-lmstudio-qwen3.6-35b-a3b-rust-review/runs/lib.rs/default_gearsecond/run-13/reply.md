**Logic & Arithmetic**
- `Warehouse::receive` (L81) uses `HashMap::insert`, which replaces existing entries. The doc comment states units should be added to `on_hand`, but the code overwrites it.
- `Warehouse::ship` (L112) and `record_loss` (L120) subtract from `on_hand` without verifying the operand fits. Debug builds panic on underflow; release builds wrap silently, corrupting inventory state.
- `deltas` (L157) iterates `0..prices.len()`, accessing `prices[i + 1]` on the final iteration. Panics with index out of bounds.

**Memory Safety & Undefined Behavior**
- `SlotTable::lookup` (L185) uses `get_unchecked` on a scanner-supplied index. Out-of-range input causes undefined behavior. Replace with `get` or an explicit bounds check.
- `append_batch` (L196) stores a raw pointer before `extend_from_slice`. If the `Vec` reallocates during the extend, the pointer dangles. Dereferencing it is UB. Read `buf[start]` after the extend instead.

**Concurrency**
- `confirm` (L258) locks `holds` then `warehouse`. `sweep_expired` (L270) locks `warehouse` then `holds`. Concurrent calls can deadlock (ABBA lock ordering). Reorder locks consistently or drop one before acquiring the other.

ISSUES:
L81: receive overwrites existing SKU instead of adding stock
L112: ship underflows on_hand without bounds check
L120: record_loss underflows on_hand without bounds check
L157: deltas index out of bounds on last iteration
L185: lookup allows out-of-bounds access via get_unchecked
L196: append_batch dereferences dangling pointer after potential Vec reallocation
L258: confirm and sweep_expired use conflicting lock ordering, causing deadlock