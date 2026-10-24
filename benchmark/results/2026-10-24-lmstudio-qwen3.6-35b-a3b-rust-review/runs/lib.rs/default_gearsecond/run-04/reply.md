**Logic & State**
- L81 `receive`: Doc says add to existing stock, but `insert` overwrites the entire `Item`. Previous `on_hand` and `reserved` are lost.
- L47 `available` & L120 `record_loss`: Use `-` which wraps silently in release mode. `saturating_sub` required to prevent underflow when `reserved > on_hand` or `lost > on_hand`.
- L127 `total_value`: Multiplies two `u64` values. `on_hand` (cast from u32) times `price_cents` (u64) can exceed `u64::MAX` when price > ~4.29B cents. Silent wrap.

**Panics & Bounds**
- L157 `deltas`: Loop `0..prices.len()` accesses `prices[i + 1]`. When `i` equals last index, `i+1` is out of bounds. Guaranteed panic.

**Unsafe / UB**
- L185 `lookup`: `get_unchecked` on untrusted scanner input skips bounds checks. Out-of-range slot causes undefined behavior.
- L194 `append_batch`: Stores raw pointer before `extend_from_slice`. Extension may reallocate the `Vec`, invalidating the pointer. Dereference at L196 is UB.

**Concurrency**
- L245 `place_hold` vs L265 `confirm`: `place_hold` locks `warehouse` then `holds`. `confirm` locks `holds` then `warehouse`. Opposite ordering creates a deadlock window on concurrent calls.

ISSUES:
L47: `available` uses `-` which wraps in release mode instead of saturating
L81: `receive` overwrites existing SKU state instead of adding to it
L120: `record_loss` uses `-` on `on_hand` which wraps in release mode
L127: `total_value` multiplication can overflow `u64`
L157: `deltas` accesses `prices[i + 1]` out of bounds on last iteration
L185: `lookup` uses `get_unchecked` on untrusted scanner input causing UB
L194: `append_batch` stores raw pointer before potential reallocation causing UB
L245: `place_hold` and `confirm` acquire `Mutex` locks in opposite order causing deadlock