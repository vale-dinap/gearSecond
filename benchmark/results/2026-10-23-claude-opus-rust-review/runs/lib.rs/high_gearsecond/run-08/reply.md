## Review of `src/lib.rs`

### Memory safety / undefined behaviour

**L185 – `SlotTable::lookup` uses `get_unchecked` on untrusted input.** The doc comment says `slot` comes straight from a handheld scanner message, and nothing validates it. Any `slot >= self.slots.len()` is an out-of-bounds read, which is UB. That makes it a remotely triggerable memory-safety bug. Use `self.slots.get(slot).copied().flatten()`. The bounds check is a single compare and won't show up in a profile.

**L194–196 – `append_batch` reads through a dangling pointer.** `first` is taken from `buf.as_ptr()` before `extend_from_slice(tail)`. If that extend reallocates, `first` points into freed memory, and `*first` at L196 is a use-after-free. This happens whenever the batch is longer than the spare capacity. Since `head` is already in hand, the pointer isn't needed: return `Some((head, buf.len()))`.

**L218 – `decode` calls `from_utf8_unchecked` on network bytes.** A `str` containing invalid UTF-8 is UB, and the doc comment says this record "is received from the network". Use `std::str::from_utf8(&rest[..len]).map_err(|_| InvError::Malformed("bad utf-8"))?`.

### Concurrency

**L259 / L262 / L265 – lock-order inversion in `Service::confirm` (deadlock).** `place_hold` (L245, L247) and `sweep_expired` (L272–273) lock `warehouse` then `holds`. `confirm` locks `holds` first and then `warehouse` while still holding `holds`. If `confirm` runs concurrently with `place_hold` or `sweep_expired`, each thread can hold one lock and wait forever for the other. Make `confirm` take `warehouse` before `holds`, like the other two methods.

**L253 – `Instant::now() + ttl` panics on overflow.** `ttl` is caller-supplied, so a very large value such as `Duration::MAX` panics, and that panic happens while both mutexes are held. Every later `.lock().unwrap()` on those mutexes then panics too, because they are poisoned. Use `Instant::now().checked_add(ttl)` and return an error when it is `None`.

### Logic errors / integer overflow / panics

**L80–81 – `receive` overwrites existing SKUs.** The doc says units are added to an existing SKU. The code instead inserts a fresh `Item`, which discards the existing `on_hand` and also resets `reserved` to 0. Outstanding reservations and holds are silently lost: a later `ship` or `confirm` of a hold fails, or `release` does nothing. Use the `entry` API and do `on_hand += qty`, preferably with `checked_add`, keeping `reserved`.

**L120 – `record_loss` can underflow and breaks the `reserved <= on_hand` invariant.** If `lost > on_hand`, the subtraction panics in debug builds and wraps to roughly 4 billion units in release builds. Even when it doesn't underflow, it can push `on_hand` below `reserved`. That then causes:

- **L47** – `available()` computes `on_hand - reserved`, which underflows. It panics in debug and in release returns a huge availability, so `reserve` over-commits stock. `low_stock` (L132) is affected the same way.
- **L112** – `ship` can underflow `on_hand` for the same reason.

Validate `lost <= on_hand`. You also need to decide how losses interact with reservations, for example by rejecting the loss or reducing `reserved`. In any case, make `available()` use `saturating_sub` or `checked_sub` as a backstop.

**L127 – `total_value` can overflow.** `on_hand as u64 * price_cents` and the following `.sum()` overflow for large prices or quantities. This panics in debug and gives a silently wrong total in release. Use `checked_mul`/`checked_add`, or accumulate in `u128`.

**L156–157 – `deltas` always panics on non-empty input.** The loop runs `i` up to `prices.len() - 1`, so `prices[i + 1]` indexes out of bounds on the last iteration. Iterate over `prices.windows(2).map(|w| w[1] - w[0])`, or loop over `0..prices.len().saturating_sub(1)`. The subtraction can also overflow for extreme `i64` values; use `checked_sub` if that matters.

**L204 – `encode` silently truncates long names.** `name.len() as u8` wraps for names of 256 bytes or more. The length prefix no longer matches the bytes written, so `decode` reads part of the name as the SKU and quantity and returns a corrupted record. Truncation can also cut a multi-byte character in half. Reject or truncate names over 255 bytes at a char boundary, and return a `Result`.

### Not flagged
- `moving_average`: the empty range when `window > len` is handled correctly.
- `parse_command`, the `Display` impls and the tests look correct.
- `next_id` overflow is not a realistic concern at `u64`.

ISSUES:
L185: `get_unchecked` with untrusted scanner-supplied slot index, out-of-bounds read (UB)
L196: dereferences pointer taken before `extend_from_slice` may reallocate, use-after-free (UB)
L218: `from_utf8_unchecked` on untrusted network bytes, invalid UTF-8 in `str` (UB)
L259: `confirm` locks `holds` then `warehouse`, opposite order to `place_hold`/`sweep_expired`, deadlock
L253: `Instant::now() + ttl` panics on overflow with caller-supplied ttl, poisoning both mutexes
L81: `receive` replaces existing item instead of adding units, losing stock and reservations
L120: `record_loss` underflows `on_hand` and can drop it below `reserved`
L47: `available()` underflows when `reserved > on_hand` (panic or huge value, causes over-reservation)
L112: `ship` can underflow `on_hand` once the invariant is broken by `record_loss`
L127: `total_value` multiplication and sum can overflow u64
L157: `deltas` indexes `prices[i + 1]` out of bounds, panics on every non-empty input
L204: `name.len() as u8` truncates names of 256 bytes or more, producing corrupt records