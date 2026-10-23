I reviewed `src/lib.rs` by reading it. I did not compile or run it, and the file is not in a git repo. The most serious problems are undefined behaviour from unchecked UTF-8 and unchecked indexing on untrusted input, a use-after-realloc in `append_batch`, a deadlock from inconsistent lock ordering, and an `deltas` function that panics on every non-empty input.

**Memory safety and undefined behaviour**

- **`src/lib.rs:218` (`decode`)**: `from_utf8_unchecked` runs on bytes from the network. Invalid UTF-8 produces a `String` that violates its invariant, which is UB. Use `std::str::from_utf8` and map the error to `InvError::Malformed`.
- **`src/lib.rs:185` (`SlotTable::lookup`)**: `get_unchecked` with a `slot` taken from scanner input is an out-of-bounds read for any slot ≥ `slots.len()`. The "hot path" comment does not justify removing the check. Use `self.slots.get(slot).copied().flatten()`.
- **`src/lib.rs:190-197` (`append_batch`)**: `first` is a raw pointer taken before `extend_from_slice`. If that call reallocates `buf`, `first` dangles and `*first` is a use-after-free. The unsafe block is also unnecessary, because the value read is just `head`. Return `head` directly.

**Panics and arithmetic**

- **`src/lib.rs:157` (`deltas`)**: the loop runs `i` over `0..prices.len()`, so `prices[i + 1]` indexes past the end on the last iteration. Every non-empty input panics. The range should be `0..prices.len() - 1`, or use `windows(2)`. The subtraction can also overflow `i64` for extreme prices.
- **`src/lib.rs:120` (`record_loss`)**: there is no check that `lost <= on_hand`, so this underflows and panics in debug builds (wraps in release). It also never checks `reserved`, so `on_hand` can drop below `reserved`.
- **`src/lib.rs:47` (`available`)**: `on_hand - reserved` underflows once `record_loss` has broken the `reserved <= on_hand` invariant. This also affects `low_stock` (`src/lib.rs:132-133`) and `reserve`, which call it.
- **`src/lib.rs:127` (`total_value`)**: `on_hand as u64 * price_cents` and the `sum` can overflow `u64` for large prices. Use `checked_mul` and `checked_add`, or `saturating_*`.
- **`src/lib.rs:253` (`place_hold`)**: `Instant::now() + ttl` panics if `ttl` is very large. Use `checked_add` and return an error.

**Logic errors**

- **`src/lib.rs:80-81` (`receive`)**: this inserts a fresh `Item`, so receiving stock for an existing SKU replaces `on_hand` and resets `reserved` to 0. The doc comment says units should be added. Existing holds then no longer match the stock, and a later `ship` can fail after the hold has already been removed.
- **`src/lib.rs:204` (`encode`)**: `name.len() as u8` silently truncates names longer than 255 bytes. The length prefix then disagrees with the bytes written, so the record is corrupt. Reject long names.

**Concurrency**

- **`src/lib.rs:245-247` vs `src/lib.rs:259-265`**: `place_hold` (and `sweep_expired`) lock `warehouse` then `holds`, but `confirm` locks `holds` then `warehouse`. If one thread is in `place_hold` holding the warehouse lock while another is in `confirm` holding the holds lock, both block forever. Pick one global lock order and use it everywhere, or hold a single lock for both maps.

**Smaller points (not listed as defects)**

- `moving_average` asserts on `window == 0`. That is a documented panic on a public API, so decide whether it should be an error.
- `release` silently clamps at zero (`saturating_sub`), which can hide double-release bugs.
- The test module covers none of the failing paths above.

I can apply fixes for the UB, panic and deadlock items if you want.

ISSUES:
L218: from_utf8_unchecked on untrusted network bytes is UB for invalid UTF-8
L185: get_unchecked with scanner-supplied slot index is out-of-bounds UB
L194: raw pointer `first` dangles if extend_from_slice reallocates buf (use-after-free)
L157: deltas indexes prices[len] and panics for every non-empty input
L157: i64 subtraction in deltas can overflow
L120: record_loss underflows on_hand and can break reserved <= on_hand
L47: available() underflows when reserved exceeds on_hand
L127: total_value u64 multiplication and sum can overflow
L204: encode truncates name length to u8, producing corrupt records for names over 255 bytes
L80: receive overwrites existing SKU instead of adding, dropping reserved and breaking holds
L253: Instant::now() + ttl panics on overly large ttl
L245: place_hold locks warehouse then holds, inverting confirm's lock order (deadlock)
L259: confirm locks holds then warehouse, inverting place_hold's lock order (deadlock)