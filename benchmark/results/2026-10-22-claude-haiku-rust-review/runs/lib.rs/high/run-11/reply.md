I reviewed the file by reading it; I did not compile or run it. The most serious problems are two undefined-behaviour sites, a lock-ordering deadlock, and unchecked arithmetic that wraps silently in release builds and can oversell stock.

## Memory safety / undefined behaviour

- **`src/lib.rs:185` (`SlotTable::lookup`)**: `get_unchecked` is called with a `slot` that the comment says comes from a scanner message. An out-of-range index is an out-of-bounds read, and since `lookup` is a safe `pub fn`, any caller can trigger it. The "hot path" justification doesn't hold up, since the bounds check is a single comparison. Use `self.slots.get(slot).copied().flatten()`.
- **`src/lib.rs:196` (`append_batch`)**: `first` points into `buf` before `extend_from_slice` at line 195. That call can reallocate, leaving `first` dangling, so the dereference is a use-after-free whenever the buffer grows. The value read is just `head`, so return `head` directly and drop the pointer.
- **`src/lib.rs:218` (`decode`)**: `from_utf8_unchecked` runs on bytes from the network. Invalid UTF-8 produces an invalid `String`, which is UB. Use `std::str::from_utf8` and map the error to `Malformed`.

## Panics, overflow, and wrong arithmetic

- **`src/lib.rs:47` (`Item::available`)**: `on_hand - reserved` underflows whenever `on_hand < reserved`. That state is reachable because `record_loss` (line 120) doesn't check reservations. In debug builds this panics; in release it wraps to about 4 billion, so `reserve` accepts quantities far beyond real stock.
- **`src/lib.rs:111-112` (`ship`)**: `reserved` is decremented before `on_hand -= qty`, which can underflow. A panic or wrap here leaves the item half-updated. Validate both counts before mutating anything.
- **`src/lib.rs:120` (`record_loss`)**: `on_hand -= lost` is unchecked and can underflow for the same oversell reason. Reject losses larger than `on_hand`.
- **`src/lib.rs:127` (`total_value`)**: the `u64` multiply and the `sum()` are unchecked. Use `checked_mul` / `checked_add` or `saturating_*`, and decide which behaviour is intended.
- **`src/lib.rs:157` (`deltas`)**: the loop runs `i` up to `len - 1` and reads `prices[i + 1]`, so it reads `prices[len]` on the last iteration. Every non-empty input panics. `prices.windows(2)` fixes the indexing. The subtraction can also overflow for extreme `i64` values.
- **`src/lib.rs:204` (`encode`)**: `name.len() as u8` silently truncates names longer than 255 bytes. The length byte then disagrees with the payload, and `decode` misparses the record without reporting an error. Reject long names.
- **`src/lib.rs:253` (`place_hold`)**: `Instant::now() + ttl` panics on overflow, for example with `Duration::MAX`. This happens after `reserve` at line 246 has already taken the stock, and while both mutex guards are held. The result is leaked reserved stock and poisoned mutexes, so every later `lock().unwrap()` panics. Compute `checked_add` before reserving.

## Concurrency

- **`src/lib.rs:259` (`confirm`)**: `confirm` locks `holds` and then `warehouse`. `place_hold` (lines 245, 247) and `sweep_expired` (lines 272, 273) lock `warehouse` and then `holds`. Two threads can each hold one lock and wait on the other, which is a deadlock. Use one lock order everywhere.
- **`src/lib.rs:266` (`confirm`)**: the hold is removed at line 260, before `ship` runs. If `ship` then fails, the hold is gone and its units stay reserved forever. Look the hold up without removing it, and remove it only after the ship succeeds.

## Logic

- **`src/lib.rs:81` (`receive`)**: `insert` replaces the existing entry, which contradicts the doc comment at lines 77-78. Stock is set to `qty` instead of added to, and `reserved` resets to 0 while live holds still reference those units. That allows overcommitment later. Use `entry(sku)` and add to `on_hand`.

## Lesser points (not in the list below)

- Every `lock().unwrap()` turns a poisoned mutex into a panic that propagates to all later callers. This amplifies the `place_hold` panic above.
- `sweep_expired` discards the `Result` from `release` at line 278. That's harmless today because SKUs are never removed, but it would hide a future bug.
- `moving_average` asserts on `window == 0`. That is a reasonable precondition, but it should be documented on the function.
- `log` (line 69) grows without bound in a long-running service.
- `vec![None; n]` in `SlotTable::new` allocates `n` entries with no upper limit. Relevant only if `n` can come from outside.
- The existing tests don't cover any of the defects above. The `reserve_and_ship`, codec round-trip, and `parse_command` tests are correct as far as I can tell.

ISSUES:
L47: available() underflows when on_hand < reserved (reachable via record_loss); wraps in release and allows overselling
L81: receive() replaces the existing entry; contradicts its doc, and resets reserved to 0 while holds are live
L112: ship() decrements reserved and then on_hand unchecked; underflow leaves the item partially updated
L120: record_loss() subtracts without checking on_hand; underflow wraps to a huge stock count
L127: total_value() unchecked u64 multiply and sum; overflow panics in debug and wraps in release
L157: deltas() indexes prices[i + 1] past the end; panics on every non-empty input
L185: lookup() uses get_unchecked on an untrusted slot index; out-of-bounds read is UB in a safe fn
L196: append_batch() dereferences a pointer that dangles after extend_from_slice reallocates; UB
L204: encode() truncates names over 255 bytes to a u8 length; produces a corrupt record silently
L218: decode() uses from_utf8_unchecked on network bytes; invalid UTF-8 yields an invalid String (UB)
L253: place_hold() Instant + ttl can overflow and panic after stock is reserved, leaking it and poisoning mutexes
L259: confirm() locks holds before warehouse, opposite to place_hold/sweep_expired; ABBA deadlock
L266: confirm() removes the hold before ship(); a failed ship permanently leaks the reservation