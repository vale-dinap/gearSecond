I found several defects that would panic, cause undefined behaviour, or corrupt data. Two are the most serious: the `append_batch` use-after-realloc and the unchecked indexing on scanner input. The stock-accounting underflows are also reachable through normal use.

## Memory safety and undefined behaviour

- **`lookup`, L185:** `get_unchecked` uses `slot` straight from a scanner message, so an out-of-range value is undefined behaviour. The "hot path" saving isn't worth it. Use `self.slots.get(slot).copied().flatten()`.
- **`append_batch`, L194-196:** `first` is a raw pointer into `buf` taken before `extend_from_slice`. That call can reallocate, so `*first` reads freed memory. The first SKU is already `head`, so return `head` and drop the pointer entirely.
- **`decode`, L218:** `from_utf8_unchecked` runs on bytes from the network. Invalid UTF-8 is undefined behaviour and yields a broken `String`. Use `std::str::from_utf8(...).map_err(|_| InvError::Malformed("bad utf-8"))?`.

## Codec

- **`encode`, L204:** `name.len() as u8` truncates names longer than 255 bytes. The length prefix then disagrees with the bytes written, so every later field is misread. Reject long names, returning `Result`, or truncate on a UTF-8 boundary.

## Stock accounting

- **`available`, L47:** `on_hand - reserved` underflows when `reserved > on_hand`. That panics in debug builds and wraps in release. `low_stock` (L132) and `reserve` (L91) call it too.
- **`record_loss`, L120:** `on_hand -= lost` has no check. A loss larger than `on_hand` panics or wraps, and a loss that drops `on_hand` below `reserved` breaks the invariant that `available` depends on.
- **`ship`, L112:** Once the invariant from L120 is broken, `on_hand -= qty` underflows. `confirm` has already removed the hold at that point, so the reservation is lost.
- **`receive`, L81:** `insert` overwrites an existing SKU, which contradicts the doc comment ("units are added"). `on_hand` is reset and `reserved` goes to 0, but live holds still point at that SKU. Later confirms then ship units that no longer exist. Use `entry(sku).or_insert(...)` and add `qty` to `on_hand`.
- **`total_value`, L127:** `on_hand as u64 * price_cents` and the `sum` can overflow `u64`. Use `checked_mul`/`checked_add`, or `saturating_*`, and decide which one is intended.
- **`release`, L101:** `saturating_sub` silently ignores over-release. That hides accounting bugs, so consider returning an error when `qty > reserved`.

## Concurrency

- **Lock order, L245 vs L259:** `place_hold` takes `warehouse` then `holds`. `confirm` takes `holds` then `warehouse`, and `sweep_expired` takes `warehouse` then `holds`. Two threads, one in `place_hold` and one in `confirm`, can deadlock. Pick one order everywhere, or hold a single mutex around the whole state.
- **Poisoning:** every `lock().unwrap()` panics on all later calls once any panic happens while a lock is held. Given the panics above, one bad input can take the service down. Either handle `PoisonError` or make the code panic-free.

## Arithmetic and logic

- **`deltas`, L156-157:** `for i in 0..prices.len()` reads `prices[i + 1]`, so the last iteration indexes past the end. Any non-empty input panics. Use `prices.windows(2).map(|w| w[1] - w[0])`, which also avoids the `i64` subtraction overflow, or use `checked_sub`.
- **`parse_command`, L305-307:** the verb is checked after the SKU and quantity are parsed. `PING 1 2` therefore reports "bad sku" or "trailing input", not "unknown verb". This is minor, but the error is misleading.

The tests cover only the happy paths. None of the defects above is caught by them.

ISSUES:
L47: available() underflows when reserved > on_hand, panicking in debug and wrapping in release
L81: receive() overwrites an existing SKU, resetting on_hand and reserved and orphaning its holds
L112: ship() underflows on_hand when on_hand < qty, which record_loss can cause
L120: record_loss() underflows on_hand when lost > on_hand and can break reserved <= on_hand
L127: total_value() multiplication and sum can overflow u64
L157: deltas() indexes prices[i + 1] at i = len-1, panicking on any non-empty input
L185: lookup() uses get_unchecked on a scanner-supplied slot, which is out-of-bounds undefined behaviour
L196: append_batch() dereferences a pointer into buf after extend_from_slice may have reallocated, which is undefined behaviour
L204: encode() truncates names longer than 255 bytes with `as u8`, corrupting the record
L218: decode() uses from_utf8_unchecked on network input, which is undefined behaviour for invalid UTF-8
L259: confirm() locks holds then warehouse, but place_hold() locks warehouse then holds, so the two can deadlock