# Review of `src/lib.rs`

There are three sources of undefined behaviour, a deadlock, and several logic and overflow bugs. In order of severity:

## Undefined behaviour / memory safety

**L185 – `SlotTable::lookup` uses `get_unchecked` on untrusted input.**
The doc comment says `slot` comes straight from a scanner message. Any `slot >= slots.len()` is an out-of-bounds read. That is UB, not a panic. A bounds check costs almost nothing here. Use `self.slots.get(slot).copied().flatten()`.

**L194–196 – `append_batch` dereferences a dangling pointer.**
`first` is taken from `buf.as_ptr()` before `buf.extend_from_slice(tail)`. That call can reallocate, which frees the old buffer, so `*first` becomes a use-after-free. There is no reason to use a pointer here. `head` is already known, so return `Some((head, buf.len()))`.

**L218 – `decode` uses `from_utf8_unchecked` on network bytes.**
A `str` holding invalid UTF-8 is UB. Later string operations can read out of bounds or misbehave. Use `std::str::from_utf8(&rest[..len]).map_err(|_| InvError::Malformed("bad utf-8"))?`.

## Concurrency

**L259/L262/L265 vs L245/L247 and L272/L273 – lock-order inversion causes deadlock.**
- `place_hold` and `sweep_expired` lock `warehouse` and then `holds`.
- `confirm` locks `holds` and then `warehouse`.

Thread A in `place_hold` can hold `warehouse` and wait for `holds`, while thread B in `confirm` holds `holds` and waits for `warehouse`. Both block forever. Pick one global order, warehouse then holds, and use it everywhere. In `confirm`, take `warehouse` first or drop `holds` before locking it.

## Logic errors

**L79–81 – `receive` overwrites an existing SKU instead of adding to it.**
The doc says units are added to what is on hand. The code calls `insert` with a fresh `Item`, so it:
- throws away the existing `on_hand`,
- resets `reserved` to 0 while holds are still outstanding, so a later `confirm`/`ship` fails with `Insufficient` and the reservation accounting is lost,
- silently replaces the name and price.

Use the `entry` API and `checked_add` on `on_hand`.

**L156–157 – `deltas` indexes past the end.**
The loop runs `i` up to `len - 1`, so `prices[i + 1]` panics on every non-empty input. The loop should be `for i in 1..prices.len()` with `prices[i] - prices[i - 1]`, or use `prices.windows(2)`. Separately, `i64` subtraction can overflow for extreme values. That panics in debug builds and wraps in release.

## Integer overflow / panics

**L120 – `record_loss` underflows `on_hand`.**
Nothing checks that `lost <= on_hand`. If it isn't, debug builds panic and release builds wrap to roughly 4 billion units. Even without underflow, it can push `on_hand` below `reserved`, which breaks the invariant everything else depends on. It should reject the call, or at least decide explicitly how losses of reserved stock are handled.

**L47 – `available()` underflows once `on_hand < reserved`.**
That state is reachable through L120. The result is a panic in debug, or a huge "available" count in release. In release, `reserve` would then happily over-reserve, and `low_stock` (L132) would misreport. L112 (`ship`) has the same exposure.

**L127 – `total_value` can overflow.**
`on_hand as u64 * price_cents` overflows for large prices (`price_cents` is an unrestricted `u64`), and so can the `sum`. Use `checked_mul`/`checked_add` and return `Option`, or widen to `u128`.

**L204 – `encode` truncates the name length.**
`name.len() as u8` silently wraps for names over 255 bytes. The resulting record decodes into a garbage name, SKU and qty. Validate the length or return an error. A truncated slice could also end mid-UTF-8, which is another reason to fix L218.

**L253 – `Instant::now() + ttl` panics on overflow.**
A very large `ttl` such as `Duration::MAX` panics. Because this happens after `reserve` succeeded at L246, the panic also poisons both mutexes. Use `checked_add` and return an error before reserving.

## Minor, related

**L260/L266 – `confirm` loses the hold if `ship` fails.**
The hold is removed before `ship` runs. If `ship` fails (most easily after the L79 bug resets `reserved`), the hold is gone but nothing is released.

ISSUES:
L185: get_unchecked with untrusted scanner slot index, out-of-bounds read (UB)
L196: pointer taken before extend_from_slice may dangle after reallocation, use-after-free (UB)
L218: from_utf8_unchecked on untrusted network bytes, invalid UTF-8 str (UB)
L259: confirm locks holds then warehouse, opposite order to place_hold/sweep_expired, deadlock
L81: receive overwrites existing item (loses on_hand, resets reserved) instead of adding units
L157: deltas indexes prices[i + 1] past the end, always panics on non-empty input
L120: record_loss subtracts without check, u32 underflow and on_hand can drop below reserved
L47: available() underflows when on_hand < reserved
L127: on_hand * price_cents and the sum can overflow u64
L204: name.len() as u8 truncates names longer than 255 bytes, corrupt record
L253: Instant::now() + ttl panics on overflow after stock is already reserved
L266: hold removed before ship; if ship fails the reservation is never released