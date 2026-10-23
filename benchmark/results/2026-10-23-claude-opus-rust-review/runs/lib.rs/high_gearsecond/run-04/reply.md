## Review of `src/lib.rs`

### Memory safety / undefined behaviour

**L185, `SlotTable::lookup`: out-of-bounds read.** `slot` comes straight from a scanner message, and `get_unchecked` with an index `>= slots.len()` is UB. Any malformed or malicious message reads arbitrary memory. Use `self.slots.get(slot).copied().flatten()`. The bounds check costs almost nothing.

**L194–196, `append_batch`: dangling pointer.** `first` is taken from `buf.as_ptr()`, then `extend_from_slice` can reallocate `buf`, freeing the old allocation. `*first` is then a use-after-free. Read the value after the extend instead (`buf[start]`), or just return `head`, which is the same value.

**L218, `decode`: unchecked UTF-8 on network input.** `from_utf8_unchecked` on bytes received from the network creates a `str`/`String` that may hold invalid UTF-8. That is UB, and later string operations can misbehave. Use `std::str::from_utf8(...).map_err(|_| InvError::Malformed("bad utf-8"))?`.

### Concurrency

**L259/L262/L265 vs L245/L247 and L272/L273: lock-order inversion, which can deadlock.**
- `place_hold` and `sweep_expired` take `warehouse` and then `holds`.
- `confirm` takes `holds` and then, while still holding it, takes `warehouse`.

If one thread is in `confirm` and another in `place_hold` or `sweep_expired`, each can end up waiting on the lock the other holds. Pick a single order everywhere, for example lock `warehouse` first in `confirm` too.

### Logic errors

**L79–81, `receive`: overwrites existing stock.** The doc says units are added to an existing SKU. Instead, `insert` replaces the whole item. That discards the current `on_hand` and resets `reserved` to 0 while holds may still be outstanding. Those holds then fail in `ship`, or silently free stock that was promised to someone. Use `entry(sku).and_modify(|i| i.on_hand += qty).or_insert(...)`, and decide whether the addition should be checked for overflow.

**L120, `record_loss`: underflow, and the stock invariant is broken.**
- `on_hand -= lost` panics in debug builds and wraps to a huge value in release when `lost > on_hand`.
- Even without underflow, it can push `on_hand` below `reserved`. After that, `available()` (L47) underflows, and `ship` (L112) can underflow `on_hand`.

Validate `lost <= on_hand`, and decide how losses interact with reservations.

**L47, `available`: unchecked subtraction.** This relies on the invariant `reserved <= on_hand`, and `record_loss` and `receive` both break that invariant. It then panics or wraps, which also breaks `reserve` and `low_stock`.

**L156–157, `deltas`: index out of bounds.** The loop runs `i` over `0..len`, so `prices[i + 1]` panics on the last iteration for any non-empty input. Loop over `0..len.saturating_sub(1)`, or use `prices.windows(2)`. The `i64` subtraction can also overflow for extreme values, so consider `checked_sub` if inputs aren't bounded.

**L204, `encode`: length truncation.** `name.len() as u8` silently truncates names longer than 255 bytes. The length prefix then disagrees with the payload, so `decode` reads part of the name as `sku`/`qty`. Either reject or truncate long names explicitly (on a UTF-8 boundary), or make `encode` return a `Result`.

### Overflow / panics on input

**L127, `total_value`: arithmetic overflow.** `on_hand as u64 * price_cents` and the `.sum()` can both overflow `u64` with large prices. That panics in debug and silently wraps in release, producing a wrong valuation. Use `checked_mul`/`checked_add`, or return `u128`.

**L253, `place_hold`: `Instant + Duration` can panic.** `Instant::now() + ttl` panics if `ttl` is huge, for example `Duration::MAX` from a client. The panic happens while the `warehouse` and `holds` mutexes are held, which poisons them, and every later `.unwrap()` on those locks then panics. Use `checked_add` and return an error.

ISSUES:
L185: `get_unchecked` with untrusted slot index, out-of-bounds read (UB)
L196: pointer into `buf` dereferenced after `extend_from_slice` may have reallocated (use-after-free)
L218: `from_utf8_unchecked` on network bytes, invalid UTF-8 String (UB)
L259: `confirm` locks holds then warehouse, opposite order to `place_hold`/`sweep_expired`, so it can deadlock
L81: `receive` overwrites existing item, losing on_hand and resetting reserved despite doc saying it adds
L120: `record_loss` can underflow on_hand and can push on_hand below reserved
L47: `available` underflows when reserved > on_hand
L157: `deltas` indexes `prices[i + 1]` past the end, panics on any non-empty input
L204: `name.len() as u8` truncates names > 255 bytes, corrupting the wire record
L127: `on_hand * price_cents` and the sum can overflow u64
L253: `Instant::now() + ttl` panics on huge ttl while holding locks, poisoning the mutexes