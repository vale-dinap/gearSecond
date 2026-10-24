**Review**

The module contains several real defects that can lead to panics, incorrect results, or undefined behaviour.  
Below is a concise description of each issue and the line numbers where it occurs.

| Line | Defect |
|------|--------|
| **47** | `Item::available` subtracts `reserved` from `on_hand`. If `reserved > on_hand` (e.g., after `record_loss`) this underflows, causing a debug‑panic or wrap‑around in release builds. |
| **120** | `Warehouse::record_loss` blindly does `item.on_hand -= lost;`. When `lost > on_hand` the subtraction underflows, producing the same panic/wrap problem as above and leaving `reserved > on_hand`, which further corrupts `available()`. |
| **157** | `deltas` iterates `for i in 0..prices.len()` but accesses `prices[i + 1]`. When `i == prices.len() - 1` the index is out of bounds, leading to a panic. |
| **185** | `SlotTable::lookup` dereferences an unchecked slice element (`*self.slots.get_unchecked(slot)`). If `slot` is out of range this is undefined behaviour and can crash or corrupt memory. |
| **194–196** | `append_batch` takes a raw pointer to the buffer before any push/extend operation, then dereferences it after possible reallocation. This results in undefined behaviour if the vector reallocates (which it will for many inputs). |
| **218** | `decode` uses `std::str::from_utf8_unchecked(&rest[..len])`. If the encoded name contains invalid UTF‑8 this is UB; the caller must validate the bytes before conversion. |
| **245 / 247 vs 259 / 261** | In `Service::place_hold` the mutexes are locked in order *warehouse → holds*, whereas `Service::confirm` locks them as *holds → warehouse*. If both functions run concurrently a deadlock can occur (each thread waits for the other’s lock). |
| **272 / 273 vs 259 / 261** | Similarly, `sweep_expired` locks *warehouse → holds* while `confirm` locks *holds → warehouse*, creating another possible deadlock scenario. |
| **204** | In `encode`, the name length is stored in a single byte (`name.len() as u8`). Names longer than 255 bytes are truncated, producing corrupted wire data. |
| **127** | `total_value` multiplies `on_hand * price_cents` into a `u64`. For large values this can overflow silently (wrap‑around), yielding an incorrect total value. |
| **80** | `Warehouse::receive` uses `self.items.insert(sku, item)` which replaces any existing entry for that SKU. If the method is called again for an existing SKU the previous inventory and reservations are lost—a logic bug rather than a safety issue but still harmful. |

---

### ISSUES
```
L47: Item::available underflows when reserved > on_hand.
L120: record_loss subtracts without bounds check, causing underflow.
L157: deltas indexes out of bounds (i+1 at last iteration).
L185: SlotTable::lookup dereferences unchecked index → UB.
L194-196: append_batch obtains pointer before push/extend; may be invalid after reallocation → UB.
L218: decode uses from_utf8_unchecked on arbitrary data → UB if bytes are not valid UTF‑8.
L245/247 vs L259/261: place_hold locks warehouse→holds, confirm locks holds→warehouse → potential deadlock.
L272/273 vs L259/261: sweep_expired locks warehouse→holds, confirm locks holds→warehouse → potential deadlock.
L204: encode truncates name length to u8 (max 255 bytes), losing data for longer names.
L127: total_value multiplication may overflow silently.
L80: receive overwrites existing SKU entry, discarding previous inventory data.
```
