The module contains several functional bugs, unchecked arithmetic that can
wrap or panic, unsafe code paths that lead to undefined behaviour, and a lock‑order
inconsistency that may deadlock the service.  The table below lists each defect
with its line number (the first line of the offending construct).

---

### Issues

```
ISSUES:
L47: Item::available subtracts reserved from on_hand without checking; if
    reserved > on_hand this underflows and corrupts state.
L81: Warehouse::receive inserts a new Item, overwriting an existing SKU
    instead of adding to its quantity.
L120: Warehouse::record_loss subtracts lost units from on_hand unchecked,
    allowing unsigned wrap‑around when loss exceeds stock.
L155-158: deltas iterates `0..prices.len()` but accesses `prices[i+1]`,
    indexing past the end and panicking on non‑empty input.
L174-179: SlotTable::lookup uses unsafe `get_unchecked` without bounds
    checking, producing UB if a caller supplies an out‑of‑range slot.
L191-198: append_batch takes a raw pointer to the first element before
    extending the vector; reallocation during `extend_from_slice` can make
    that pointer dangling, leading to UB when dereferenced.
L245-252: Service::place_hold locks `warehouse` then `holds`, while
    Service::confirm and Service::sweep_expired lock them in the opposite
    order.  This inconsistent lock ordering can cause a deadlock between
    threads holding one lock each.
```
