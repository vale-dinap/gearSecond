## Review of `src/lib.rs`

I reviewed the code by reading it. I did not compile it or run the tests.

### Undefined behaviour and memory safety

- **`SlotTable::lookup` (L183-186):** `get_unchecked` uses a slot number that the doc comment says comes from a scanner message. Any `slot >= len` reads past the end of the Vec's buffer. The "hot path" comment doesn't justify removing the check. Use `self.slots.get(slot).copied().flatten()`.
- **`decode` (L218):** `from_utf8_unchecked` runs on bytes from the network. Invalid UTF-8 produces a `String` that breaks its invariant, which is UB. Use `std::str::from_utf8` and return `Malformed` on error.
- **`append_batch` (L190-197):** `first` is a raw pointer into `buf`'s allocation, taken at L194. `extend_from_slice` at L195 can reallocate the buffer, and L196 then dereferences the stale pointer. This is a use-after-free whenever the Vec grows. The pointer is also unnecessary, because `head` already holds the value. Return `head`.

### Panics and overflow

- **`Item::available` (L47):** `on_hand - reserved` underflows when `reserved > on_hand`. That state is reachable through `record_loss` (see below). It panics in debug and wraps in release, which makes `available()` huge and lets over-reservation through.
- **`record_loss` (L120):** `on_hand -= lost` has no bound check. It underflows the same way. Also, it doesn't check `reserved`, so it can create the state above.
- **`ship` (L112):** `on_hand -= qty` underflows. The check at L108 only compares against `reserved`, so a loss that left `on_hand < reserved` passes the check and then underflows. Example: on_hand 5, reserved 5, loss 3, then ship 5 passes L108 and underflows at L112.
- **`deltas` (L156-157):** The loop runs `i` over `0..prices.len()` and reads `prices[i + 1]`. On the last iteration that index is `len`, so every non-empty input panics. The `i64` subtraction can also overflow. Use `prices.windows(2).map(|w| w[1].checked_sub(w[0]))`, or handle the overflow explicitly.
- **`total_value` (L127):** `on_hand as u64 * price_cents` can overflow `u64`, and so can the `sum()`. Use `checked_mul` and `checked_add`, or widen to `u128`.

### Logic

- **`receive` (L79-81):** `HashMap::insert` replaces the existing item, which resets `reserved` to 0 and sets `on_hand` to `qty`. The doc comment says units are added to existing stock. Outstanding holds then have no stock behind them, which allows overselling. Use the entry API and do `on_hand += qty`.
- **`encode` (L204):** `name.len() as u8` silently truncates names longer than 255 bytes. The length byte then disagrees with the bytes written, so the frame is corrupt. Return an error for long names, or truncate at a char boundary. Changing the return type to `Result` allows the error to be reported.

### Concurrency

- **Lock-order inversion:** `place_hold` takes `warehouse` then `holds` (L245, then L247). `confirm` takes `holds` then `warehouse` (L259, then L262 or L265). If one thread is in `place_hold` holding `warehouse` and another is in `confirm` holding `holds`, both wait forever. Pick one order everywhere, or merge the two into a single mutex. Also, `next_id` (L249) is a third lock taken inside the other two. An `AtomicU64` would remove it.
- **Lock poisoning:** Every `.unwrap()` on a lock means one panic, such as the overflows above, makes all later calls panic too. Removing the panics is the real fix.

### Not defects, but worth noting

- `log` (L69) grows without bound in a long-running service.
- The `assert!` in `moving_average` (L144) is a documented panic, so it is fine as written.

ISSUES:
L47: available() underflows when reserved > on_hand; panics in debug, wraps in release
L81: receive() replaces existing item, resetting reserved and on_hand instead of adding
L112: ship() on_hand -= qty underflows when a loss has left on_hand below reserved
L120: record_loss() subtracts without bound check; underflows and ignores reserved
L127: total_value() u64 multiplication and sum can overflow
L157: deltas() reads prices[i + 1] out of bounds on last iteration; panics on any non-empty input
L185: lookup() uses get_unchecked on scanner-supplied slot; out-of-bounds read (UB)
L196: append_batch() dereferences pointer invalidated by extend_from_slice reallocation (UB)
L204: encode() truncates name length to u8; frame corrupt for names over 255 bytes
L218: decode() from_utf8_unchecked on untrusted bytes; UB on invalid UTF-8
L259: confirm() locks holds then warehouse, inverting place_hold order (L245); deadlock risk