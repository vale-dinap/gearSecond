**Summary of problems**

The module contains several logical errors that can lead to panics or undefined behaviour (UB), integer overflows, and a dead‑lock risk in the thread‑safe `Service` type.

| Problem | Why it matters |
|---------|----------------|
| **Item::available underflow** – subtracts `reserved` from `on_hand` without checking that `reserved <= on_hand`. After a loss or an incorrect ship/receive, this can wrap to a huge value. | Can make inventory counts wrong and break invariants used elsewhere. |
| **Warehouse::receive replaces existing items** – inserting a SKU always overwrites any previous entry, discarding the current stock and reservations. | Makes it impossible to add more units to an existing product. |
| **Warehouse::ship can underflow on_hand** – `item.on_hand -= qty` is executed without ensuring that the shelf has enough units (the code only checks `reserved`). | Can produce a huge wrapped value or panic in debug builds. |
| **Warehouse::record_loss can underflow on_hand** – simply subtracts `lost` from `on_hand`. | Similar to ship; loss may exceed current stock. |
| **total_value overflows silently** – multiplies two `u64`s without checking that the product fits into `u64`. | Inventory value can wrap, giving a wrong total. |
| **deltas panics on the last element** – iterates over all indices and accesses `i+1`, which is out of bounds for the final iteration. | Causes a runtime panic on normal use. |
| **append_batch UB** – obtains a raw pointer to the buffer before extending it, then uses that pointer after possible reallocation (`wrapping_add` + deref). The pointer may become dangling or wrap around. | Undefined behaviour; can crash or corrupt memory. |
| **encode truncates long names** – casts `name.len()` to `u8` without bounds checking. | Names longer than 255 bytes are silently truncated, producing an invalid wire format. |
| **decode uses unchecked UTF‑8 conversion** – `from_utf8_unchecked` can produce a `String` that violates Rust’s guarantee that all strings are valid UTF‑8. | UB if the input contains invalid UTF‑8. |
| **Service lock ordering is inconsistent** – `place_hold` locks `warehouse` then `holds`, while `confirm` and `sweep_expired` lock `holds` first and then `warehouse`. This can deadlock when two threads call these methods concurrently. | Prevents the service from being used safely in a multithreaded context. |

---

### ISSUES
```
L47: Item::available may underflow if reserved > on_hand.
L80: Warehouse::receive overwrites an existing SKU, losing stock and reservations.
L111: Warehouse::ship subtracts from on_hand without checking that on_hand >= qty.
L120: Warehouse::record_loss can underflow on_hand when lost > current stock.
L127: total_value multiplies u64 values without overflow checks; may wrap silently.
L157: deltas accesses i+1 for the last index, causing a panic.
L194: append_batch uses wrapping_add to compute a raw pointer before reallocation; unsafe and can wrap.
L196: append_batch dereferences that possibly dangling pointer; UB if buffer reallocates.
L204: encode casts name length to u8 without bounds checking; names >255 bytes are truncated.
L218: decode performs unchecked UTF‑8 conversion, producing an invalid String (UB).
L247: place_hold locks holds while holding warehouse lock – inconsistent order with confirm.
L265: confirm locks warehouse after already holding holds – inconsistent ordering may deadlock.
```