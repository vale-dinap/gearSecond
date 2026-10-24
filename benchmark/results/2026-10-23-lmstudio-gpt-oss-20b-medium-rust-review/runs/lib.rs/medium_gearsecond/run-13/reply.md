The module contains several real‑world defects that can lead to panics, data corruption, or deadlocks.  
Below are the key problems grouped by their nature:

* **Unchecked arithmetic** – subtraction on unsigned integers may underflow and cause a panic (debug) or wrap‑around (release).  
* **Incorrect logic in `receive`** – existing SKUs are overwritten instead of having their quantity increased.  
* **Potential underflows in stock manipulation** – `ship`, `record_loss`, and `reserve` can reduce counters below zero.  
* **Overflow potential** – adding to `reserved` or multiplying values for the total value may overflow a 32‑bit or 64‑bit integer without checks.  
* **Bounds/UB issues** – unsafe unchecked indexing in `SlotTable::lookup`, unsafe UTF‑8 conversion in `decode`, and an out‑of‑bounds loop in `deltas`.  
* **Deadlock risk** – the locking order in `Service` is inconsistent between `place_hold`, `confirm`, and `sweep_expired`, allowing a classic deadlock scenario.

---

### ISSUES:
```
L47: self.on_hand - self.reserved may underflow (panic/wrap)
L79: receive overwrites existing SKU instead of adding quantity
L112: item.on_hand -= qty can underflow when shipping too many units
L120: item.on_hand -= lost can underflow on record_loss
L156: deltas loops to len causing out‑of‑bounds access
L185: lookup uses unsafe get_unchecked, UB if slot out of range
L218: decode uses from_utf8_unchecked, UB on invalid UTF‑8
L245-247: place_hold locks warehouse then holds (ordering A)
L259-266: confirm locks holds then warehouse (ordering B) – deadlock possible
L271-276: sweep_expired locks warehouse then holds (ordering A) – deadlock with confirm
```