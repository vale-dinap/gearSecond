The module shouldn't merge as written. Three spots are undefined behaviour on inputs that a scanner or the network can supply, and `deltas` panics on any non-empty input.

## Undefined behaviour and memory safety

**`SlotTable::lookup` (L183–186):** `get_unchecked` is called with `slot`, which the doc comment says comes from a scanner message. An out-of-range value is an out-of-bounds read, which is UB. The bounds check is a single compare and isn't worth removing here. Use `self.slots.get(slot).copied().flatten()`.

**`append_batch` (L194–197):** `first` is a pointer into `buf` taken before `buf.extend_from_slice(tail)` at L195. That call can reallocate, which leaves `first` dangling, and L196 dereferences it. The value read is just `head`, so the fix is to drop the pointer and the `unsafe` block and return `Some((head, buf.len()))`.

**`decode` (L218):** `from_utf8_unchecked` runs on bytes from the network. Invalid UTF-8 produces a `String` that breaks its own invariant, and any later use is UB. Use `std::str::from_utf8(...).map_err(|_| InvError::Malformed("name not UTF-8"))?`.

## Panics and overflow

**`deltas` (L156–157):** The loop runs `i` over `0..prices.len()` but reads `prices[i + 1]`, so the final iteration reads `prices[len]` and panics. Any input with at least one element hits this. The `with_capacity` line uses `saturating_sub(1)`, which suggests the loop bound was meant to be `len - 1`. `prices.windows(2).map(|w| w[1] - w[0])` avoids the issue. The `i64` subtraction can also overflow for extreme prices (panic in debug, silent wrap in release), so use `checked_sub` or document the behaviour.

**`record_loss` (L120):** `on_hand -= lost` is unchecked. Losing more than is on hand panics in debug builds and wraps to about 4 billion in release builds, which makes `available()` huge and leads to overselling. It also doesn't check `reserved`, so it can push `on_hand` below `reserved`. That breaks the invariant that `available()` (L47) and `reserve` (L95) depend on. Use `checked_sub` and return `Insufficient`, and decide whether losses may eat into reserved units.

**`total_value` (L127):** `on_hand as u64 * price_cents` and the `.sum()` can both overflow, because `price_cents` is a full `u64`. Use `checked_mul`/`checked_add`, `saturating_*`, or `u128`.

**`place_hold` (L253):** `Instant::now() + ttl` panics when `ttl` is very large. Use `checked_add` and return an error.

## Logic errors

**`receive` (L80–81):** The doc says units are added to an existing SKU, but `insert` replaces the entry. `on_hand` becomes `qty` rather than increasing, `reserved` resets to 0 while holds are still outstanding, and the name and price are overwritten. For example, with `on_hand = 10` and a hold of 5, a restock of 10 leaves `on_hand = 10, reserved = 0`. That makes 5 units oversold, and the hold later fails in `ship`. Use the entry API and add to `on_hand`.

**`confirm` (L260, L266):** The hold is removed before shipping. If `ship` fails, the reservation is lost and nothing restores it. Re-insert the hold on failure.

**`encode` (L204):** `name.len() as u8` truncates names longer than 255 bytes, but the full name is still written. The length prefix is wrong, so `decode` reads the SKU and quantity from the wrong offsets and returns garbage without an error. Return a `Result` or reject long names in `receive`.

**`Warehouse::log` (L69):** Every mutating call pushes a `String` and nothing ever trims it. This is a slow leak for a long-running service.

## Concurrency

**Lock-order inversion (L245–247, L259–265, L272–273):** `place_hold` and `sweep_expired` take the warehouse lock and then the holds lock. `confirm` takes the holds lock and then the warehouse lock. If one thread is in `place_hold` holding the warehouse lock while another is in `confirm` holding the holds lock, both block forever. Pick one order and use it everywhere, or put the warehouse and holds behind a single mutex. The `unwrap()` calls on the locks also turn one panic into a poisoned-lock panic on every later call. That's a reasonable choice, but it should be deliberate.

## Not defects

The reserve/ship arithmetic is correct as long as the `reserved <= on_hand` invariant holds. The bugs above are what break it. `parse_command`, `sweep_expired`, and `snapshot` look correct.

The existing tests don't reach any of the failing paths. Before merging, add tests for `deltas` with length 0 and 1, `record_loss` beyond `on_hand`, `lookup` out of range, `decode` with invalid UTF-8, `encode` with a name over 255 bytes, and a concurrent `confirm`/`place_hold` run.

ISSUES:
L81: receive replaces the existing entry instead of adding stock, resetting reserved to 0 while holds are outstanding
L120: record_loss subtracts without a check, so it underflows (panic or wrap) and can drop on_hand below reserved
L127: total_value can overflow in the u64 multiply and in the sum
L157: deltas reads prices[len] on the last iteration and panics for any non-empty input
L157: deltas i64 subtraction can overflow for extreme price values
L185: lookup uses get_unchecked on an untrusted slot index, an out-of-bounds read (UB)
L196: append_batch dereferences a pointer that extend_from_slice can invalidate by reallocating (UB)
L204: encode truncates the name length to u8, producing corrupt records for names over 255 bytes
L218: decode uses from_utf8_unchecked on network input, creating an invalid String (UB)
L253: place_hold panics when Instant + ttl overflows for a very large ttl
L262: confirm takes warehouse while holding holds, the reverse of place_hold and sweep_expired, which can deadlock
L266: confirm removes the hold before shipping, so a failed ship silently loses the reservation
L69: Warehouse log grows without bound