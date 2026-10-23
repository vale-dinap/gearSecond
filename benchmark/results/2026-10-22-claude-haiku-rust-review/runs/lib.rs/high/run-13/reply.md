I found several serious defects. Three are undefined behaviour on inputs that can be untrusted, and one is a deadlock.

## Undefined behaviour / memory safety

**`lookup`, L185.** `get_unchecked` is called with a `slot` that the doc comment says comes from a handheld scanner. Any out-of-range slot is an out-of-bounds read, which is UB. The bounds check is cheap, so the "hot path" justification doesn't hold. Fix: `self.slots.get(slot).copied().flatten()`.

**`append_batch`, L193-196.** `first` points into `buf` before `extend_from_slice`. If the extend reallocates, which it will whenever capacity is exceeded, `first` dangles and L196 is a use-after-free. The unsafe block is also unnecessary, since the first SKU is just `head`. Fix: `let &head = batch.first()?; buf.extend_from_slice(batch); Some((head, buf.len()))`.

**`decode`, L218.** `from_utf8_unchecked` runs on network bytes with no validation. A `String` holding invalid UTF-8 is UB, and later operations on it can be UB too. Fix: `std::str::from_utf8(&rest[..len]).map_err(|_| InvError::Malformed("invalid utf-8"))?.to_string()`.

## Concurrency

**Lock-order inversion, L245-265.** `place_hold` and `sweep_expired` lock `warehouse` then `holds`. `confirm` locks `holds` (L259) and then `warehouse` (L262 or L265). If `confirm` holds `holds` while `place_hold` holds `warehouse`, each waits on the other and the service deadlocks. Fix: take the locks in one global order everywhere, for example `warehouse` before `holds`, which means `confirm` must lock `warehouse` first.

Related: every `lock().unwrap()` poisons the mutex if a holder panics. Because of the arithmetic panics below, one bad `ship` could make every later call panic.

## Panics and arithmetic

**`deltas`, L156-157.** The loop runs `i` up to `len - 1` and reads `prices[i + 1]`, so it indexes `prices[len]` and panics on every non-empty input. Fix: `prices.windows(2).map(|w| w[1] - w[0]).collect()`. Also consider `checked_sub`, because the i64 subtraction can overflow for extreme values.

**`available` and `record_loss`, L47 and L120.** `record_loss` subtracts `lost` from `on_hand` with no check, and it ignores reservations. It can therefore leave `on_hand < reserved`, and then `available()` underflows. In debug builds that panics. In release builds it wraps to about 4 billion, so `reserve` accepts any quantity. Fix: have `record_loss` reject `lost > on_hand - reserved` (or `lost > on_hand`) with an error, and keep the invariant `reserved <= on_hand`.

**`ship`, L111-112.** It checks `qty <= reserved` but not `qty <= on_hand`. It decrements `reserved` first and then `on_hand`, so an underflow in the second step leaves the item half-updated. Fix: check both before mutating anything.

**`total_value`, L127.** `on_hand as u64 * price_cents` and the `sum()` are unchecked u64 arithmetic. This needs unit prices above about $42.9M to overflow a single product, but nothing prevents it. Use `checked_mul`/`checked_add`, or widen to `u128`.

**`encode`, L204.** `name.len() as u8` truncates the length for names longer than 255 bytes, but L205 still writes the full name. The receiver then reads a corrupt record. Fix: return `Result` and reject names that don't fit, using `u8::try_from(name.len())`.

## Logic

**`receive`, L80-81.** The doc says units are added to existing stock, but `insert` replaces the whole item. `on_hand` is set to `qty` and `reserved` is reset to 0. Outstanding holds then no longer match `reserved`, so a later `confirm` can fail with `Insufficient`, and the hold is lost. Fix: use `entry(sku)` and add to `on_hand` for existing SKUs, keeping `reserved` and `name` as they are.

**`confirm`, L260.** The hold is removed before the fallible `ship` or `release` runs. If `ship` fails, the hold is gone but its units stay reserved, and nothing releases them. Fix: validate first, then remove the hold, or put it back on failure.

**`log`, L69 and L82.** The log grows without bound in a long-running service. Cap it or rotate it.

Smaller notes, not in the list: `Service::new` accepts a warehouse that may already hold reservations with no matching hold, so those units are never released. `moving_average` asserts on `window == 0` without a `# Panics` note. The tests cover none of the defects above.

ISSUES:
L81: receive() overwrites the existing item instead of adding to on_hand, resetting reserved to 0 so outstanding holds no longer match
L185: lookup() uses get_unchecked on an untrusted scanner index, an out-of-bounds read (UB)
L196: append_batch() dereferences a pointer invalidated by extend_from_slice reallocation (use-after-free, UB)
L218: decode() calls from_utf8_unchecked on untrusted bytes; invalid UTF-8 in a String is UB
L204: encode() truncates the name length to u8 but writes the full name, producing corrupt records for names over 255 bytes
L157: deltas() indexes prices[i + 1] up to len, panicking on every non-empty input
L259: confirm() locks holds then warehouse, while place_hold (L245) and sweep_expired (L272) lock warehouse then holds, which can deadlock
L47: available() underflows when reserved > on_hand, reachable through record_loss; wraps in release and lets reserve() accept any quantity
L120: record_loss() subtracts without checking on_hand or reservations, panicking or wrapping
L112: ship() decrements on_hand after reserved without checking qty <= on_hand, which can leave partial state
L127: total_value() multiplies and sums in unchecked u64, which can overflow for large unit prices
L260: confirm() removes the hold before the fallible ship/release, so a failed ship loses the hold and leaves its units reserved
L82: log Vec grows without bound in a long-running service