I found 13 defects. Four of them are undefined behaviour reachable from `unsafe` blocks, and one is a deadlock between `Service` methods. The rest are logic errors, panics and integer overflows.

## Undefined behaviour

**`SlotTable::lookup` (L185).** `get_unchecked(slot)` skips the bounds check. The doc comment says `slot` comes straight from a handheld scanner, so a bad scan reads out of bounds, which is UB. Use `self.slots.get(slot).copied().flatten()`. The bounds check is a single compare and isn't worth removing.

**`append_batch` (L194–196).** `first` is a raw pointer into `buf`'s heap allocation. `extend_from_slice(tail)` on L195 can reallocate that buffer, which leaves `first` dangling. Dereferencing it on L196 is then a use-after-free. The value is already known, so return `head` and drop the pointer and the `unsafe` block.

**`decode` (L218).** `from_utf8_unchecked` runs on bytes "received from the network". Building a `str` from invalid UTF-8 is UB, and any later string operation can misbehave. Use `std::str::from_utf8(...).map_err(|_| InvError::Malformed("bad utf-8"))?`.

## Concurrency

**Lock-order inversion between `confirm` and the other `Service` methods (L259 vs L245/L247 and L272/L273).**
- `place_hold` and `sweep_expired` take `warehouse` first, then `holds`.
- `confirm` takes `holds` first (L259), then `warehouse` (L262 or L265).

If `confirm` runs at the same time as `place_hold` or `sweep_expired`, each thread can end up holding one lock while waiting for the other, and both block forever. Pick one global order, for example warehouse then holds, everywhere. Alternatively, in `confirm`, remove the hold, drop the `holds` guard, and only then lock `warehouse`.

## Logic errors

**`Warehouse::receive` (L80–81).** The doc says units for an existing SKU are added to what is on hand. Instead, `insert` replaces the whole `Item`. Two things go wrong:
- Existing `on_hand` is lost.
- `reserved` is reset to 0 while holds for that SKU are still outstanding. Those holds' later `ship` then fails, and their `release` is silently swallowed by `saturating_sub`.

Use `entry(sku)`: add to `on_hand` (checked) when the SKU exists, and insert a new `Item` only when it doesn't.

## Panics and integer overflow

**`Item::available` (L47).** `on_hand - reserved` underflows whenever `reserved > on_hand`. That state is reachable through `record_loss` (see below). The result is a panic in debug builds and a huge bogus availability in release builds, which would let `reserve` over-reserve.

**`Warehouse::ship` (L112).** `on_hand -= qty` is checked only against `reserved`, not `on_hand`. Once a loss has pushed `on_hand` below `reserved`, this underflows.

**`Warehouse::record_loss` (L120).** `on_hand -= lost` has no check at all. Two failures follow:
- `lost > on_hand` underflows (panic in debug, wrap in release).
- Even a valid loss can leave `on_hand < reserved`, which breaks the invariant that L47 and L112 rely on.

It should reject `lost > on_hand`, or reject `lost > available()`, or clamp `reserved` to the new `on_hand`.

**`Warehouse::total_value` (L127).** `on_hand as u64 * price_cents` and the `.sum()` can both overflow `u64` when prices are large. Use `checked_mul`/`checked_add` (or `u128`) and report the overflow.

**`deltas` (L156–157).** The loop runs `i` up to `len - 1` and reads `prices[i + 1]`. That is out of bounds on the last iteration, so the function panics for every non-empty input. The loop should be `for i in 1..prices.len()`, or use `prices.windows(2)`. Separately, `prices[i+1] - prices[i]` can overflow `i64` for extreme values; `checked_sub` fixes that.

**`Service::place_hold` (L253).** `Instant::now() + ttl` panics if `ttl` is huge. By that point `reserve` has already run (L246), and the reservation is never undone. Use `checked_add` and validate it before reserving.

## Wire format

**`encode` (L204).** `name.len() as u8` silently truncates names longer than 255 bytes. The length byte then disagrees with the name bytes, and `decode` reads the wrong bytes as the name, SKU and quantity. Reject over-long names or truncate the name itself; a fallible `encode` is the cleaner option.

ISSUES:
L185: get_unchecked on untrusted scanner slot index is out-of-bounds read (UB)
L196: raw pointer read after extend_from_slice may have reallocated buf (use-after-free, UB)
L218: from_utf8_unchecked on network bytes is UB for invalid UTF-8
L259: confirm locks holds then warehouse, opposite order to place_hold/sweep_expired, so it can deadlock
L81: receive overwrites existing item, losing on_hand and resetting reserved despite outstanding holds
L47: available() underflows when reserved > on_hand (panic or bogus huge availability)
L112: ship subtracts from on_hand without checking it, so it can underflow
L120: record_loss underflows on_hand and can leave on_hand < reserved
L127: on_hand * price_cents and the sum can overflow u64
L157: deltas indexes prices[i + 1] past the end and panics on any non-empty input; subtraction can overflow
L253: Instant::now() + ttl can panic after the reservation was already made, leaking it
L204: name.len() as u8 truncates names over 255 bytes, corrupting the record