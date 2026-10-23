I reviewed this by reading it. I haven't compiled it or run the tests. The most serious problems are the undefined-behaviour cases (`lookup`, `decode`, `append_batch`) and the lock-order deadlock in `confirm`.

## Memory safety and undefined behaviour

- **`lookup` (L185):** `get_unchecked` takes a slot number from a scanner message. Any index at or past `slots.len()` reads out of bounds, which is UB and can leak heap contents. The unsafe block isn't needed: `self.slots.get(slot).copied().flatten()` is just as cheap and safe.
- **`decode` (L218):** `from_utf8_unchecked` runs on bytes from the network. Invalid UTF-8 produces a `String` that violates its invariants. Use `std::str::from_utf8(...)` and map the error to `Malformed`.
- **`append_batch` (L194–196):** `first` is taken before `extend_from_slice`, which can reallocate `buf`. The dereference at L196 then reads freed memory. It only fails when a reallocation happens, so small tests will pass. The read is also pointless: the value is just `head`, so return `(head, buf.len())`.

## Panics and arithmetic

- **`available` (L47):** `on_hand - reserved` underflows once `reserved > on_hand`. That state is reachable through `record_loss`. In debug builds it panics. In release builds (overflow checks off by default) it wraps to about 4 billion. `low_stock` then stops reporting the SKU, and `reserve` can over-reserve.
- **`record_loss` (L120):** `on_hand -= lost` is unchecked. Losing more than is on hand panics or wraps. It also doesn't clamp `reserved`, which is what creates the state above.
- **`ship` (L112):** `on_hand -= qty` has the same underflow. It is reachable after a loss has pushed `on_hand` below `reserved`.
- **`deltas` (L157):** `prices[i + 1]` runs one index past the end on the last iteration. Every non-empty input panics, e.g. `deltas(&[5])`. Use `prices.windows(2).map(|w| w[1] - w[0]).collect()`. The `i64` subtraction can also overflow on extreme values, so `checked_sub` is worth considering.
- **`total_value` (L127):** `on_hand as u64 * price_cents` and the `sum` can overflow `u64` (`u32::MAX` times a large price). Use checked or saturating arithmetic.
- **`place_hold` (L253):** `Instant::now() + ttl` panics when the result is out of range, which a very large `Duration` can cause. Use `checked_add` and return an error.
- **`encode` (L204):** `name.len() as u8` truncates the length byte for names over 255 bytes, but all the name bytes are still written. The record is corrupt and the decoder misparses everything after the name. Return an error for long names.

## Logic and concurrency

- **`receive` (L80–81):** `insert` replaces the existing item. This contradicts the doc comment, which says units are added. It drops the existing `on_hand` and resets `reserved` to 0, so outstanding holds stop being counted and stock can be over-reserved. Use the entry API and add to `on_hand`.
- **Deadlock (L259 / L262 / L265):** `confirm` locks `holds` and then `warehouse`. `place_hold` (L245→L247) and `sweep_expired` (L272→L273) lock `warehouse` and then `holds`. If one thread is in `confirm` and another is in `place_hold` or `sweep_expired`, each can hold one lock and wait for the other. Pick one order and use it everywhere.
- **Hold removed before the fallible step (L260 → L266):** `confirm` removes the hold before `ship`, which can fail. If it does, the hold is gone and its units stay reserved forever. With the current `Service` API this looks unreachable, but validating first and removing the hold on success is safer.

## Also worth addressing

- Every `.lock().unwrap()` turns one panic into a poisoned mutex that takes down the whole service. Decide on a policy, such as recovering with `into_inner()` or propagating an error.
- `log` grows without bound in a long-running process (L82, L113, L121).
- `moving_average` panics on `window == 0`. That's documented, but returning a `Result` would be friendlier to callers.
- The tests cover none of these paths. Useful additions: `deltas` on `[]`, `[x]` and `[a, b]`; `append_batch` with a batch large enough to reallocate; `encode` with a 300-byte name; `decode` with invalid UTF-8; `record_loss` past `on_hand`; and concurrent `place_hold`/`confirm`/`sweep_expired`. Running `cargo +nightly miri test` over the unsafe paths should catch the UB cases.

ISSUES:
L47: available() subtracts u32 unchecked; underflows when reserved > on_hand, wrapping silently in release
L80: receive() replaces the existing item, dropping on_hand and reserved counts despite documented add semantics
L112: ship() does on_hand -= qty unchecked; underflows when on_hand is below reserved
L120: record_loss() does on_hand -= lost unchecked; underflows when lost > on_hand
L127: total_value() multiplication and sum can overflow u64
L157: deltas() indexes prices[i + 1] past the end; panics on every non-empty input
L185: lookup() uses get_unchecked on a scanner-supplied index; out-of-bounds read (UB)
L196: append_batch() dereferences a pointer invalidated by extend_from_slice reallocation (UB)
L204: encode() truncates names longer than 255 bytes via `as u8`, producing a corrupt record
L218: decode() uses from_utf8_unchecked on untrusted bytes; UB on invalid UTF-8
L253: place_hold() Instant + ttl panics on overflow for very large ttl
L259: confirm() locks holds before warehouse, opposite to place_hold/sweep_expired; deadlock