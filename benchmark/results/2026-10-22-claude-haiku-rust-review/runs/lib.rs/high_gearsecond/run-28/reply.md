I reviewed this by reading only. I did not compile it or run the tests.

**Memory safety / undefined behaviour**

- **L185 `lookup`**: `get_unchecked` uses a slot number that comes from a scanner message, with no bounds check. An out-of-range slot is an out-of-bounds read, and the function is a safe `pub fn`, so callers can't avoid it. The "hot path" comment doesn't justify it. Use `self.slots.get(slot).copied().flatten()`.
- **L218 `decode`**: `from_utf8_unchecked` runs on bytes from the network. Invalid UTF-8 produces a `String` that breaks Rust's invariants, which is UB. Use `std::str::from_utf8` and return `Malformed` on error.
- **L194–197 `append_batch`**: `first` points into `buf` and is taken after `push`. `extend_from_slice` can reallocate the buffer, which leaves `first` dangling, so `*first` is a use-after-free read. The function only needs `head`, so it should return `Some((head, buf.len()))` with no `unsafe`.

**Panics and arithmetic**

- **L47 `available()`**: `on_hand - reserved` underflows when `reserved > on_hand`. That state is reachable through `record_loss`. In debug builds it panics; in release it wraps to a huge available count.
- **L120 `record_loss`**: `on_hand -= lost` underflows when `lost > on_hand`. It also doesn't check `reserved`, so `on_hand` can drop below `reserved`. That breaks the invariant that `available()` and `ship()` (L112) rely on.
- **L127 `total_value`**: both the `u64` multiply and the `sum()` are unchecked and can overflow. Use checked or `u128` arithmetic.
- **L157 `deltas`**: `prices[i+1] - prices[i]` overflows for distant `i64` values. Use `checked_sub` or widen to `i128`.
- **L253 `place_hold`**: `Instant::now() + ttl` panics if `ttl` is very large. Use `checked_add` and return an error.

**Logic**

- **L81 `receive`**: the doc says units are added to an existing SKU, but `insert` replaces the whole item. Receiving stock for an existing SKU resets `reserved` to 0 while holds are still live, which allows overbooking. It also overwrites the name and price. Use an entry API and add to `on_hand` with checked arithmetic.
- **L204 `encode`**: `name.len() as u8` silently truncates names longer than 255 bytes. The length byte then disagrees with the payload and the decoder reads the wrong bytes. Reject long names, or return a `Result`.
- **L101 `release`**: `saturating_sub` hides over-release instead of reporting it, so bugs in callers stay silent.

**Concurrency**

- **L259 `confirm`**: this locks `holds` and then `warehouse` (L262, L265). `place_hold` (L245, L247) and `sweep_expired` (L272–273) lock `warehouse` and then `holds`. Two threads can deadlock: one in `confirm` holds `holds` and waits for `warehouse`, while another in `place_hold` holds `warehouse` and waits for `holds`. Pick one lock order everywhere, or merge the two mutexes.
- Every `.unwrap()` on a lock turns one panic into a panic in every later caller, because the mutex is poisoned. This is lower severity, but it's worth handling if the service has to stay up.

**Resource and design notes (lower severity)**

- **L82 / L121 / L113**: `log` grows without bound for the life of the process. Cap it or ship it somewhere.
- Nothing calls `sweep_expired` automatically. Until something does, expired holds keep stock reserved indefinitely.

ISSUES:
L47: `available()` underflows when reserved exceeds on_hand, reachable after record_loss
L81: `receive` replaces the existing item, resetting reserved and overwriting on_hand instead of adding
L101: `release` saturates silently, hiding over-release
L120: `record_loss` underflows on_hand and can leave on_hand below reserved
L127: `total_value` overflows on the multiply and the sum
L157: `deltas` i64 subtraction overflows for distant values
L185: `lookup` uses get_unchecked on untrusted slot, giving an out-of-bounds read (UB)
L196: `append_batch` reads through a pointer that dangles after extend_from_slice reallocates (UB)
L204: `encode` truncates name length to u8, corrupting records over 255 bytes
L218: `decode` uses from_utf8_unchecked on untrusted bytes (UB)
L253: `place_hold` panics on Instant overflow for a huge ttl
L259: `confirm` takes holds then warehouse, opposite to place_hold and sweep_expired, so the two can deadlock
L82: `log` grows without bound in a long-running process