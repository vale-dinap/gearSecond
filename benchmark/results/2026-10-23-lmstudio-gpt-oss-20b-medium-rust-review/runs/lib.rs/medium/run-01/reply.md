**Major defects found**

| Area | What’s wrong | Why it matters |
|------|--------------|----------------|
| `Item::available` (line 47) | Uses subtraction without checking that `reserved ≤ on_hand`.  If the invariant is violated (e.g., after a manual change or a bug in `record_loss`) this will underflow and panic. | Causes silent crashes when inventory data becomes inconsistent. |
| `Warehouse::total_value` (line 127) | Computes `on_hand as u64 * price_cents`.  The product can exceed `u64::MAX`, wrapping silently in release builds or panicking in debug builds. | Over‑estimates value and can corrupt statistics. |
| `Warehouse::record_loss` (line 120) | Directly subtracts `lost` from `on_hand` without bounds checking.  If `lost > on_hand`, the field underflows. | Leads to negative stock counts and later panics when shipping or reserving. |
| `Warehouse::ship` (line 112) | Subtracts `qty` from `on_hand` after verifying only that `qty ≤ reserved`.  If a prior loss reduced `on_hand` below `reserved`, this will underflow. | Crash during normal operation when inventory has been damaged or stolen. |
| `deltas` (lines 156‑158) | Iterates `for i in 0..prices.len()` and accesses `prices[i + 1]`.  The last iteration (`i = len-1`) reads past the slice, causing a panic. | The function never works correctly for non‑empty price lists. |
| `SlotTable::lookup` (line 185) | Uses `get_unchecked(slot)` without bounds checking and returns an `Option<Sku>` that is actually dereferenced.  Out‑of‑range indices trigger undefined behaviour. | Hot path may crash or corrupt memory if callers forget to validate the slot number. |
| `append_batch` (lines 194‑196) | Stores a raw pointer (`first`) obtained from `buf.as_ptr()` *before* mutating the vector with `push`.  If `push` reallocates, that pointer becomes dangling and reading it is UB. | Causes silent data corruption or crashes in production. |
| `Service::confirm` vs `sweep_expired` (lines 259 & 272) | The two methods lock `holds` and `warehouse` in opposite orders: `confirm` locks `holds` first, then `warehouse`; `sweep_expired` locks `warehouse` first, then `holds`.  This ordering mismatch can deadlock when the two threads run concurrently. | The service may become permanently stuck, refusing new holds or sweeps. |

**Other minor concerns**

* `encode` truncates names longer than 255 bytes (line 204).  
* `next_id` can wrap around after `u64::MAX` holds are created, but this is unlikely in practice.

---

### ISSUES
L47: `Item::available` may underflow if `reserved > on_hand`.  
L120: `record_loss` subtracts without bounds checking; can underflow `on_hand`.  
L112: `ship` subtracts from `on_hand`; may underflow if inventory is already below reserved.  
L127: `total_value` multiplies two values that can overflow a `u64`.  
L156‑158: `deltas` iterates one step too far, accessing out of bounds and panicking.  
L185: `SlotTable::lookup` dereferences an unchecked index; out-of-range causes UB.  
L194: `append_batch` stores a raw pointer before possible reallocation; reading it is undefined behaviour.  
L259 & 272: inconsistent lock order between `confirm` and `sweep_expired` can lead to deadlock.