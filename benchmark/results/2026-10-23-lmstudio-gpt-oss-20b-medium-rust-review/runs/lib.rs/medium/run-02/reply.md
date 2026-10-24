The module contains several real‑world defects that can lead to panics, undefined behaviour or deadlocks.  
Below is a brief discussion of each class of problem followed by a concise list of the offending lines.

### Summary of Issues

| Category | Description |
|----------|-------------|
| **Arithmetic/logic** | `Item::available` subtracts without checking that `reserved <= on_hand`.  Combined with `record_loss`, this can underflow.  `total_value` multiplies two u64 values which may overflow silently. |
| **Business‑rule violations** | `receive` replaces an existing SKU instead of adding to it, violating the comment and potentially losing stock/reservations. |
| **Missing bounds checks** | `record_loss` allows `lost > on_hand`.  `deltas` indexes past the end of a single‑element slice. |
| **Unsafe code / UB** | `SlotTable::lookup` uses `get_unchecked` with no bounds check.  `append_batch` dereferences a pointer that may have been invalidated by a reallocation.  `decode` calls `from_utf8_unchecked` without validating the data. |
| **Encoding/decoding bugs** | `encode` truncates names longer than 255 bytes (`u8`). |
| **Concurrency / deadlock risk** | `Service::place_hold` locks `warehouse` then `holds`, while `confirm` locks them in the opposite order, creating a potential deadlock. |

---

## ISSUES

```
L47: Item::available subtracts on_hand - reserved without ensuring no underflow.
L80-81: receive() replaces an existing SKU instead of adding to it; loses stock/reservations.
L120: record_loss() subtracts lost from on_hand without checking that lost <= on_hand, causing underflow.
L155-L157: deltas() loops over all indices but accesses i+1, which panics for any non‑empty slice (single element).
L185: SlotTable::lookup() uses unsafe get_unchecked without bounds checking → UB if slot out of range.
L196: append_batch() dereferences a pointer that may have been invalidated by reallocation → UB.
L204: encode() casts name.len() to u8, silently truncating names >255 bytes and breaking round‑trip.
L218: decode() uses unsafe from_utf8_unchecked on raw data; if the buffer is not valid UTF‑8 this is UB.
L127: total_value() multiplies two u64 values that may overflow silently (wraps).
L245-L255 vs L259-267: Service::place_hold locks warehouse before holds, while confirm locks holds first → potential deadlock when called concurrently.
```

These defects should be addressed before merging to ensure correct, safe, and predictable behaviour.