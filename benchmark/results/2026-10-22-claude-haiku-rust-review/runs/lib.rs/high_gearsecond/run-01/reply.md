## Review of `src/lib.rs`

I found several real defects. The most serious are two cases of undefined behaviour (L185 and L194-196), a deadlock (L247 and L259), and an unchecked UTF-8 conversion on network input (L218). The rest are panics, overflow, and silent data corruption.

### Undefined behaviour

**`append_batch` (L190-198): use-after-free.** `first` is a pointer into `buf` taken before `extend_from_slice(tail)`. That call can reallocate the vector, which leaves `first` dangling, and L196 then dereferences it. The function only needs to return `head`, so the fix is to drop the pointer entirely: `Some((head, buf.len()))`.

**`SlotTable::lookup` (L183-186): out-of-bounds read.** `slot` comes from a scanner message, and `get_unchecked` skips the bounds check. Any slot `>= n` is UB. The "hot path" comment does not justify this. Use `self.slots.get(slot).copied().flatten()`, which costs a single bounds check.

**`decode` (L218): unchecked UTF-8 on untrusted bytes.** `from_utf8_unchecked` on network input yields an invalid `String` if the bytes are not UTF-8, which is UB. Use `std::str::from_utf8(...).map_err(|_| InvError::Malformed("bad utf-8"))?`.

### Deadlock

**Lock-order inversion in `Service` (L247, L259, L265, L272-273).** `place_hold` takes `warehouse` then `holds` (L245, L247). `confirm` takes `holds` then `warehouse` (L259, L262/L265). If one thread is in `place_hold` and another is in `confirm`, each can hold one lock and wait for the other. `sweep_expired` (warehouse then holds) has the same problem against `confirm`. Pick one global order (warehouse, then holds, then next_id) and use it everywhere. In `confirm`, take the warehouse lock first, or restructure so both locks are never held at once in opposite orders.

### Panics and overflow

**`Item::available` (L47):** `on_hand - reserved` underflows when `reserved > on_hand`. Panics in debug builds and wraps in release. `record_loss` can produce that state (see below).

**`record_loss` (L118-123):** `on_hand -= lost` has no check. Losing more than is on hand underflows, and the function never verifies that `reserved <= on_hand` still holds after the loss. Clamp or reject, and check that `lost <= on_hand - reserved`.

**`ship` (L111-112):** `on_hand -= qty` relies on the invariant `reserved <= on_hand`, which `record_loss` breaks. Once that invariant is gone, this underflows too.

**`total_value` (L127):** `on_hand as u64 * price_cents` and the `sum()` can overflow `u64`. Use `checked_mul` and `checked_add`, or `saturating_*`, and return an error or `Option`.

**`deltas` (L157):** `prices[i + 1] - prices[i]` overflows `i64` for extreme inputs. Use `checked_sub` or widen to `i128`.

**`place_hold` (L253):** `Instant::now() + ttl` panics for a very large `ttl`. Use `checked_add` and return an error.

### Logic and data integrity

**`receive` (L79-82):** `HashMap::insert` replaces the whole `Item`. The doc says units are added to existing stock, but the code sets `on_hand` to `qty`, resets `reserved` to 0 (so live holds are no longer tracked), and overwrites the name and price. Use `entry(sku).and_modify(|i| i.on_hand += qty).or_insert(...)` with an overflow check. Note that the doc also needs updating if the intent is to keep the existing name and price.

**`encode` (L204-205):** `name.len() as u8` truncates names longer than 255 bytes. The length byte then disagrees with the bytes written, so `decode` reads the wrong fields. Reject names over 255 bytes with an error.

**`release` (L101):** `saturating_sub` silently hides over-releases, which masks accounting bugs. It is not a crash, so this is a judgement call, but it is worth reconsidering.

### Lower-severity observations

- `Mutex::lock().unwrap()` throughout `Service` propagates poisoning as a panic. This is a design choice, but it is worth documenting.
- `decode` ignores trailing bytes after the record, which can hide framing errors.
- `Service::new` builds a default `Warehouse` and then discards it. This is harmless.

ISSUES:
L47: available() underflows when reserved > on_hand (panic in debug, wrap in release)
L81: receive() replaces the whole item, resetting reserved and overwriting name and price, despite doc saying units are added
L120: record_loss() has no bounds check; underflows and can break reserved <= on_hand
L112: ship() on_hand -= qty underflows once reserved <= on_hand is broken by record_loss
L127: total_value() u64 multiply and sum can overflow
L157: deltas() i64 subtraction overflows for extreme prices
L185: lookup() get_unchecked with scanner-supplied index is out-of-bounds UB
L194: append_batch() pointer taken before reallocating extend
L196: append_batch() dereferences possibly dangling pointer (use-after-free UB)
L204: encode() truncates name length to u8 for names over 255 bytes, corrupting the wire format
L218: decode() from_utf8_unchecked on untrusted network bytes is UB for invalid UTF-8
L247: place_hold() takes holds lock while holding warehouse; inverted order vs confirm() causes deadlock
L253: place_hold() Instant + ttl panics on overflow for large ttl