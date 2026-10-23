Several of these are serious: four separate undefined-behaviour bugs in `unsafe` blocks, one deadlock, and a few panics and logic errors in the stock arithmetic.

## Undefined behaviour

**`SlotTable::lookup` (L185).** `get_unchecked` is called with a `slot` that, per the doc comment, comes straight from a handheld scanner. Any out-of-range value is an out-of-bounds read, which is UB. That is a real memory-safety hole on untrusted input, not just a wrong answer. Use `self.slots.get(slot).copied().flatten()`; the bounds check costs next to nothing.

**`append_batch` (L194–196).** `first` is a raw pointer into the buffer, taken before `extend_from_slice`. If the extend has to grow the `Vec`, the buffer is reallocated and `first` dangles, so `*first` is a use-after-free. No `unsafe` is needed: `head` is already the value, so return `Some((head, buf.len()))`.

**`decode` (L218).** `from_utf8_unchecked` runs on bytes "received from the network". Building a `str` from invalid UTF-8 is UB, and later string operations can read out of bounds. Use `std::str::from_utf8(..).map_err(|_| InvError::Malformed("bad utf-8"))?`.

## Concurrency

**Lock-order inversion (L245/247 vs L259/262/265).** `place_hold` and `sweep_expired` lock `warehouse` then `holds`. `confirm` locks `holds` first and then `warehouse` while still holding `holds`. If `confirm` runs at the same time as `place_hold` or `sweep_expired`, the two threads can deadlock. `confirm` should take `warehouse` first, matching the other two.

## Logic errors and panics

**`receive` (L80–81) overwrites instead of adding.** The doc says units are added to an existing SKU, but `insert` replaces the whole `Item`. This loses the current `on_hand` and also resets `reserved` to 0 while holds may still be outstanding. A later `confirm` then fails in `ship` with `Insufficient`, after the hold has already been removed (L260), so that reservation is silently lost. Use the entry API (`or_insert_with`), then `on_hand = on_hand.checked_add(qty)`.

**`record_loss` (L120) can underflow, and breaks the invariant `on_hand >= reserved`.**
- If `lost > on_hand`, the subtraction panics in debug builds and wraps to roughly 4 billion units in release.
- Even when `lost <= on_hand`, it can push `on_hand` below `reserved`. The function needs to validate `lost` and also decide what happens to reservations.

**`Item::available` (L47) and `ship` (L112) underflow.** Once `on_hand < reserved`, which `record_loss` allows:
- `available()` panics or wraps. It is also called from `reserve` and from `low_stock` (L132–133).
- `ship` checks only `qty <= reserved`, so `on_hand -= qty` can underflow too.

**`deltas` (L157) always panics on non-empty input.** The loop runs `i` up to `len - 1`, so `prices[i + 1]` indexes past the end on the last iteration. It should be `for i in 1..prices.len()` with `prices[i] - prices[i - 1]`, or `prices.windows(2)`. The `i64` subtraction can also overflow for extreme values; use `checked_sub` if inputs are not bounded.

**`total_value` (L127) can overflow.** `on_hand as u64 * price_cents` and the `sum()` are both unchecked. A large price times a large quantity panics in debug and silently wraps in release. Use `checked_mul`/`checked_add`, or `u128`/saturating arithmetic, depending on the semantics you want.

**`encode` (L204) truncates the name length.** `name.len() as u8` wraps for names of 256 bytes or more. The encoder then writes the full name with a wrong length prefix, so `decode` reads part of the name as the SKU and quantity. It may also split a UTF-8 character, which is exactly what then hits the L218 UB. Reject or cap long names, and return a `Result`.

**`place_hold` (L253): `Instant::now() + ttl` panics on overflow.** This happens for a huge `ttl` such as `Duration::MAX`. The stock has already been reserved at L246, and the panic happens while both mutexes are held. The reservation leaks and the mutexes are poisoned, so every later `.lock().unwrap()` panics. Use `checked_add` and validate before reserving.

**Minor note.** `release` (L101) silently saturates. A `RELEASE` command can free units that belong to an outstanding hold, and the hold's later `ship` then fails. Consider returning an error when `qty > reserved` rather than masking the mismatch.

ISSUES:
L185: `get_unchecked` with untrusted scanner index; out-of-bounds read is UB
L196: dereferences pointer taken before `extend_from_slice` may reallocate; use-after-free
L218: `from_utf8_unchecked` on network bytes; UB on invalid UTF-8
L259: `confirm` locks `holds` then `warehouse`, opposite order to `place_hold`/`sweep_expired`; deadlock
L81: `receive` replaces existing item, losing `on_hand` and resetting `reserved` (doc says add)
L120: `record_loss` underflows when `lost > on_hand` and can leave `on_hand < reserved`
L47: `available()` underflows when `reserved > on_hand`
L112: `ship` can underflow `on_hand` (only `reserved` is checked)
L157: `deltas` indexes `prices[i + 1]` past the end; always panics on non-empty input
L127: `on_hand * price_cents` and `sum` can overflow `u64`
L204: `name.len() as u8` truncates names >= 256 bytes, corrupting the record
L253: `Instant::now() + ttl` can panic after stock is reserved, leaking the reservation and poisoning the mutexes