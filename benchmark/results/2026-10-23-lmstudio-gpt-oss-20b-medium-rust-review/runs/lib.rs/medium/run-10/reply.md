**General review**

The module implements a very small inventory system with a handful of helper functions.  
Most of the code is straightforward, but there are several non‑trivial defects that
can lead to incorrect behaviour, panics, overflows or deadlocks.  
Below you’ll find an explanation of each class of problems followed by a concise
list of line‑numbered issues.

---

### 1. Logical / business‑rule errors

| Problem | Why it matters |
|---------|----------------|
| **`Warehouse::receive` overwrites existing SKUs** (lines 79‑81) | The comment says “for an existing SKU the units are added to what is already on hand”, but `HashMap::insert` replaces the old entry.  Existing inventory and reservations are lost, which can cause incorrect stock counts or loss of reserved items. |
| **No overflow checks when updating counters** (reserve, ship, record_loss) | Adding or subtracting from `u32` fields (`reserved`, `on_hand`) without bounds checking can wrap around silently.  In particular: <br>• `item.reserved += qty;` (line 95)<br>• `item.on_hand -= qty;` in `ship` (lines 111‑112) – if the invariant is broken this underflows.<br>• `item.on_hand -= lost;` in `record_loss` (line 120) – can underflow when `lost > on_hand`. |
| **`total_value` may overflow `u64`** (line 127) | The product of `on_hand * price_cents` is cast to `u64` and summed.  For very large inventories or high prices the sum can exceed `u64::MAX`, causing a wrap‑around. |
| **`deltas` iterates one step too far** (lines 156‑158) | The loop runs for `i in 0..prices.len()` but accesses `prices[i+1]`.  When `i == prices.len()-1` this is an out‑of‑bounds read that panics. |
| **`encode` truncates long names** (line 204) | `name.len() as u8` silently discards any length above 255, producing corrupted data for longer product names. |

---

### 2. Undefined behaviour / unsafe code

| Problem | Why it matters |
|---------|----------------|
| **Unsafe bounds‑unchecked lookup in `SlotTable::lookup`** (line 185) | It dereferences a pointer without checking that `slot < slots.len()`.  If called with an out‑of‑range index the program will crash or read arbitrary memory. |
| **Use of `unsafe` for UTF‑8 conversion in `decode`** (line 218) | While not strictly UB, it accepts any byte slice as a string, producing potentially invalid Unicode data that later operations might misbehave on. |

---

### 3. Concurrency / deadlock risks

| Problem | Why it matters |
|---------|----------------|
| **Inconsistent lock ordering between `Service::place_hold`, `confirm` and `sweep_expired`** (lines 245‑251, 259‑266, 272‑281) | `place_hold` locks `warehouse` first then `holds`; `confirm` locks `holds` first then `warehouse`.  If two threads call these functions simultaneously they can deadlock.  The same ordering mismatch appears in `sweep_expired`. |

---

### 4. Miscellaneous

| Problem | Why it matters |
|---------|----------------|
| **Missing bounds check for `SlotTable::lookup`** (duplicate of unsafe issue) | Same as above – emphasised because the public API promises safety. |
| **Potential overflow in `moving_average` sum conversion to `f64`** (line 148) | Not a hard bug but can lose precision if the daily counts are huge; not critical for typical use but worth noting. |

---

## ISSUES

```
L80: Warehouse::receive overwrites existing SKU instead of adding quantity.
L95: Reserve adds qty to reserved without checking for u32 overflow.
L111-L112: Ship subtracts from on_hand without ensuring on_hand >= qty, risking underflow.
L120: Record_loss subtracts lost from on_hand without bounds check, can underflow.
L127: total_value sum may overflow u64 when inventory or prices are large.
L156-158: deltas iterates out of bounds (i+1 access at end).
L185: SlotTable::lookup uses unsafe get_unchecked without bounds checking.
L204: encode truncates product name length to 8 bits, corrupting names >255 bytes.
L245-L251 + L259-L266 + L272-L281: inconsistent lock ordering in Service can deadlock concurrent hold placement and confirmation/sweep operations.
```