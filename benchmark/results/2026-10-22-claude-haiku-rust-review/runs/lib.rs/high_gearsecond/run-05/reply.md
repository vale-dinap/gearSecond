The most serious problems are a deadlock, two undefined-behaviour sites reachable from untrusted input, and a `receive` bug that can oversell stock. Ordered by severity:

**Deadlock and concurrency**

- **L259 (`confirm`) vs L245 (`place_hold`) and L272 (`sweep_expired`):** lock order is inconsistent. `place_hold` and `sweep_expired` take `warehouse` then `holds`. `confirm` takes `holds` then `warehouse` (L262, L265). If one thread is in `confirm` holding `holds` while another is in `place_hold` holding `warehouse`, each waits on the other forever. Fix: pick one global order (warehouse, then holds, then next_id) and use it in every method, or put all state behind one mutex.
- **L253 (`place_hold`):** `Instant::now() + ttl` panics on overflow, for example with `Duration::MAX` from a client. This happens after `wh.reserve` at L246 has already succeeded, so the stock stays reserved with no hold. The panic also poisons the `warehouse` mutex. Use `Instant::now().checked_add(ttl)` and return an error before reserving.

**Undefined behaviour and memory safety**

- **L185 (`SlotTable::lookup`):** `get_unchecked` on a slot index that the doc says comes from a scanner message. Any out-of-range value is an out-of-bounds read. Use `self.slots.get(slot).copied().flatten()`. The hot-path comment does not justify removing the check.
- **L194–197 (`append_batch`):** `first` is a raw pointer taken before `extend_from_slice(tail)`. That call can reallocate `buf`, so `*first` reads freed memory. The value is just `head`, so return `Some((head, buf.len()))` and drop the pointer entirely.
- **L218 (`decode`):** `from_utf8_unchecked` runs on bytes from the network. Invalid UTF-8 creates a `String` that violates its invariant, which is UB. Use `std::str::from_utf8(...).map_err(|_| InvError::Malformed("bad utf-8"))?`.

**Panics and integer arithmetic**

- **L157 (`deltas`):** the loop runs `i` over `0..prices.len()` and reads `prices[i + 1]`. On the last iteration that index is `len`, so every non-empty input panics, including a single element. Iterate `prices.windows(2)` or `0..prices.len().saturating_sub(1)`. The `i64` subtraction can also overflow for extreme inputs.
- **L120 (`record_loss`):** `on_hand -= lost` is unchecked. Losing more than is on hand underflows (panic in debug, wrap in release). The function also never reduces `reserved`, so `on_hand` can fall below `reserved`.
- **L47 (`available`):** `on_hand - reserved` underflows once `record_loss` breaks the invariant `reserved <= on_hand`. This panics inside `reserve` (L91) and `low_stock` (L132–133). Either make `record_loss` reject losses above `available()`, or use `saturating_sub` here and report the discrepancy.
- **L112 (`ship`):** `on_hand -= qty` depends on the same invariant, so it underflows once L120 breaks it. Fixing L120 covers this.
- **L127 (`total_value`):** `on_hand as u64 * price_cents` and the `sum` can overflow `u64` for large prices. Use `checked_mul` and `checked_add`, or document the bound.
- **L204 (`encode`):** `name.len() as u8` silently truncates names longer than 255 bytes. The length prefix is then wrong and the frame is corrupt. Reject such names with an error.
- **L144 (`moving_average`):** `assert!` panics on `window == 0` from a public function. The doc comment does not mention this. Return an empty `Vec` or a `Result` instead.

**Logic errors**

- **L80–81 (`receive`):** the doc says units are added to an existing SKU, but `insert` replaces the whole item. `on_hand` becomes `qty`, `reserved` becomes 0, and the name and price are overwritten. Active holds stay in the `holds` map while their reservation disappears, so the warehouse can oversell. A later `ship` for those holds then fails with `Insufficient`, after the hold was already removed at L260. Fix: use `entry(sku).or_insert_with(...)` and add `qty` to `on_hand`.

Minor, not blocking: `log` grows without bound, and `parse_command` checks the verb last, so `FOO 1` reports "bad qty" rather than "unknown verb".

The test module covers only the happy path. None of the defects above would be caught by it.

ISSUES:

L80: receive replaces the existing item, dropping on_hand units, reservations and holds; doc says it adds

L157: deltas indexes prices[i + 1] with i up to len-1, so any non-empty input panics; i64 subtraction can also overflow

L185: get_unchecked on untrusted slot index is an out-of-bounds read (UB)

L194: raw pointer `first` is taken before extend_from_slice, which can reallocate; dereferencing it is use-after-free

L204: name.len() as u8 truncates names over 255 bytes, producing a corrupt frame

L218: from_utf8_unchecked on network bytes creates an invalid String (UB)

L253: Instant::now() + ttl can panic after stock is reserved, leaking the reservation and poisoning the warehouse mutex

L259: confirm takes holds then warehouse, while place_hold and sweep_expired take warehouse then holds; lock-order inversion can deadlock

L47: available() underflows once reserved exceeds on_hand, panicking reserve and low_stock

L120: record_loss subtracts without checking, underflowing on_hand and breaking reserved <= on_hand

L127: total_value multiplication and sum can overflow u64 for large prices

L144: moving_average asserts on window == 0 in a public API