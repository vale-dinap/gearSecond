## Defects

### Undefined behaviour (fix first)

**L185, `SlotTable::lookup`:** `get_unchecked(slot)` takes `slot` straight from scanner input. Any `slot >= slots.len()` is undefined behaviour. The bounds check is cheap, so drop the unsafe:
```rust
pub fn lookup(&self, slot: usize) -> Option<Sku> {
    self.slots.get(slot).copied().flatten()
}
```

**L194–197, `append_batch`:** `first` points into `buf` before `extend_from_slice`, which can reallocate. `*first` then reads freed memory. The head value is already known, so return it directly:
```rust
buf.push(head);
Some((head, buf.len()))
```

**L218, `decode`:** `from_utf8_unchecked` runs on network bytes. Invalid UTF-8 produces a `String` that breaks its invariant. Validate instead:
```rust
let name = std::str::from_utf8(&rest[..len])
    .map_err(|_| InvError::Malformed("bad utf-8"))?
    .to_string();
```

### Panics and overflow

**L157, `deltas`:** the loop runs `0..prices.len()` and reads `prices[i + 1]`, so the last iteration indexes `prices[len]` and panics. Any non-empty input panics, including `[5]`. Use `prices.windows(2).map(|w| w[1] - w[0])`. The subtraction can also overflow `i64` for extreme inputs; use `checked_sub` if that matters.

**L47, `Item::available`:** `on_hand - reserved` underflows when `reserved > on_hand`. Nothing enforces that invariant. `record_loss` (L120) and `receive` (L80) can break it. In debug the call panics; in release it wraps to roughly 4 billion, and `reserve` then accepts oversell.

**L120, `record_loss`:** `on_hand -= lost` is unchecked, so it panics in debug and wraps in release when `lost > on_hand`. It also ignores `reserved`, so `on_hand` can drop below outstanding reservations. Reject `lost > on_hand - reserved` or return an error.

**L112, `ship`:** `on_hand -= qty` underflows for the same reason once the invariant is broken.

**L127, `total_value`:** `on_hand as u64 * price_cents` and the `sum` are both unchecked. A large price overflows. Use `checked_mul` and `checked_add`, or accumulate in `u128`.

### Logic

**L80, `receive`:** the doc says units are added to an existing SKU, but `insert` replaces the whole item. That resets `reserved` to 0 and overwrites `on_hand`, `name` and `price`. Outstanding holds then lose their reservation count, so `available()` overstates stock, and later `ship` calls for those holds underflow at L112. Add to the existing entry:
```rust
match self.items.get_mut(&sku) {
    Some(item) => item.on_hand = item.on_hand.checked_add(qty).ok_or(...)?, // error type TBD
    None => { self.items.insert(sku, Item { sku, name: name.to_string(), on_hand: qty, reserved: 0, price_cents }); }
}
```
The overflow case needs an error path, so `receive` should return `Result`.

**L101, `release`:** `saturating_sub` hides over-release. A double release silently frees stock that belongs to another hold. Return an error when `qty > reserved`.

**L204, `encode`:** `name.len() as u8` wraps for names over 255 bytes. The length prefix then disagrees with the bytes written, and the receiver misparses everything after it. Return a `Result` and reject names longer than `u8::MAX`.

### Concurrency

**L259 vs L245/L247, deadlock:** lock order is inconsistent.
- `place_hold`: `warehouse` (L245), then `holds` (L247), then `next_id` (L249)
- `sweep_expired`: `warehouse` (L272), then `holds` (L273)
- `confirm`: `holds` (L259), then `warehouse` (L262, L265)

Thread A in `confirm` holds `holds` and waits for `warehouse`. Thread B in `place_hold` holds `warehouse` and waits for `holds`. That deadlocks. Pick one order and use it everywhere. Since `place_hold` and `sweep_expired` already take `warehouse` first, `confirm` should lock `warehouse` before `holds`. Merging the three mutexes into one state struct would also remove the risk. `next_id` could be an `AtomicU64`.

### Tests

The existing tests cover none of these paths. Add cases for `deltas(&[5])`, `lookup` out of range (run under Miri), `receive` twice on one SKU, `record_loss` beyond `on_hand`, `encode` with a 300-byte name, and `decode` with invalid UTF-8.

ISSUES:
L47: available() underflows when reserved > on_hand
L80: receive replaces existing SKU (resets reserved/on_hand/name/price) instead of adding stock
L101: release saturates silently, hiding over-release
L112: ship underflows on_hand once stock invariant is broken
L120: record_loss underflows on_hand and can drop it below reserved
L127: total_value u64 multiply/sum overflow
L157: deltas reads prices[len], panics on every non-empty input
L157: deltas i64 subtraction overflows for extreme values
L185: get_unchecked on scanner-supplied slot is undefined behaviour
L194: stale pointer read after extend_from_slice may reallocate (use-after-free)
L204: encode truncates name length to u8, producing corrupt frames
L218: from_utf8_unchecked on network input is undefined behaviour
L259: confirm locks holds then warehouse, place_hold locks warehouse then holds: deadlock