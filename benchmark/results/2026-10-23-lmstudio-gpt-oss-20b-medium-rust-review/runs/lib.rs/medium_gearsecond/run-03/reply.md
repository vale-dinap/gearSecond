The module contains several real defects that can lead to panics, overflows, undefined behaviour or deadlocks.  
Below is a concise list of the problems identified with their line numbers.

```
ISSUES:
L95: reserve addition may overflow u32 (no bounds check)
L120: record_loss subtract may underflow on_hand
L127: total_value multiplication can overflow u64
L156-158: deltas loops past end of slice (out‑of‑bounds access)
L185: lookup uses unsafe unchecked indexing → UB if slot out of range
L192-197: append_batch takes a pointer before reallocation; may become dangling after extend_from_slice
L259: inconsistent lock ordering (holds first, then warehouse) can deadlock with place_hold or sweep_expired
```
