# Review of `src/lib.rs`

There are three undefined-behaviour bugs, a lock-order deadlock, and several arithmetic bugs that can panic or corrupt stock counts. Ordered roughly by severity:

## Undefined behaviour (memory safety)

**L185 – `SlotTable::lookup` uses `get_unchecked` on untrusted input.**
The doc comment says `slot` comes straight from a scanner message. Any `slot >= slots.len()` reads out of bounds, which is UB: garbage data, a crash, or an info leak. Use `self.slots.get(slot).copied().flatten()`. A bounds check costs almost nothing next to a `HashMap` lookup.

**L194–196 – `append_batch` reads through a dangling pointer.**
`first` is taken from `buf.as_ptr()` before `extend_from_slice(tail)`. If the extend reallocates, `first` points into freed memory and `*first` is a use-after-free. It isn't even needed, because the value is `head`. Return `Some((head, buf.len()))` and drop the `unsafe`.

**L218 – `decode` calls `from_utf8_unchecked` on network bytes.**
A `str` holding invalid UTF-8 is UB, and later string operations can misbehave. Use `std::str::from_utf8(&rest[..len]).map_err(|_| InvError::Malformed("bad utf-8"))?`.

## Concurrency

**L259/L262/L265 vs L245/L247 and L272/L273 – lock-order inversion causes deadlock.**
- `place_hold` and `sweep_expired` lock `warehouse` and then `holds`.
- `confirm` locks `holds` and then, while still holding it, locks `warehouse`.

If `confirm` runs at the same time as either of the others, each thread can hold one lock while waiting forever for the other. Pick one global order (warehouse → holds) and use it everywhere. Merging both maps under a single `Mutex` would also fix it.

**Poisoning amplifies every panic below.** All locks are taken with `.unwrap()`. Any arithmetic panic while a guard is held (e.g. L112 inside `confirm`) poisons the mutex, and every later call on the `Service` then panics. One bad request can take down the whole service.

## Logic errors and integer overflow

**L80–81 – `receive` overwrites instead of adding.**
The doc says units are added to existing stock, but `insert` replaces the whole `Item`. Two effects:
- Previous `on_hand` is lost.
- `reserved` is reset to 0 while holds are still outstanding.

Later, `confirm` → `ship` for those holds fails with `Insufficient`, after the hold has already been removed (L260). Use `entry(sku)` and do `on_hand += qty`, preferably `checked_add`.

**L120 – `record_loss` underflows and breaks the stock invariant.**
- `lost > on_hand` makes `on_hand -= lost` panic in debug builds and wrap to about 4 billion in release.
- Even without wrapping, it can push `on_hand` below `reserved`, which sets off the next two bugs.

It should validate `lost <= on_hand` and decide what happens to reservations the remaining stock can no longer cover, e.g. clamp `reserved` or reject the loss.

**L47 – `available()` underflows when `reserved > on_hand`.**
That state is reachable through L120. In release builds the result wraps to a huge value, so `reserve` (L91–95) lets callers reserve stock that doesn't exist. In debug builds it panics, including from `low_stock` (L132–133). Use `saturating_sub`, and fix the root cause in `record_loss`.

**L112 – `ship` can underflow `on_hand`.**
The only check is `qty <= reserved`. If a loss has left `on_hand < reserved`, `on_hand -= qty` panics or wraps. Inside `Service::confirm` this panic also poisons the mutex.

**L156–157 – `deltas` always indexes out of bounds.**
The loop runs `i` up to `len - 1`, so `prices[i + 1]` panics on the last iteration for any non-empty input. Use `prices.windows(2).map(|w| w[1] - w[0])`. Note that `i64` subtraction can also overflow on extreme values; use `checked_sub` if inputs are untrusted.

**L127 – `total_value` can overflow.**
`on_hand as u64 * price_cents` and the `.sum()` are both unchecked. With large prices or many SKUs this panics in debug and silently wraps in release, giving a wrong valuation. Accumulate in `u128` or use `checked_mul`/`checked_add`.

**L204 – `encode` silently truncates name length.**
`name.len() as u8` wraps for names longer than 255 bytes. The length byte then disagrees with the payload, and `decode` reads part of the name as `sku`/`qty`, so the record is silently corrupted. Reject or truncate long names explicitly, using `u8::try_from(name.len())`. If you truncate, do it on a UTF-8 char boundary.

**L253 – `Instant::now() + ttl` panics on overflow.**
A very large `ttl` (e.g. `Duration::MAX`) panics while both the `warehouse` and `holds` locks are held. That poisons both mutexes, and the reservation from L246 has already been applied and is never released. Use `checked_add` and return an error, or clamp `ttl`.

**L246 vs L253 – reservation leaks if the hold isn't recorded.**
`reserve` runs first, and nothing undoes it if a later step fails or panics, as with L253. Validate everything before calling `reserve`.

ISSUES:
L185: `get_unchecked` with untrusted scanner slot index causes out-of-bounds read (UB)
L196: pointer taken before `extend_from_slice` may dangle after reallocation; use-after-free (UB)
L218: `from_utf8_unchecked` on network input yields invalid `str` (UB)
L259: `confirm` locks holds→warehouse while `place_hold`/`sweep_expired` lock warehouse→holds; deadlock
L245: `.unwrap()` on locks means any panic while a guard is held poisons the mutex and bricks the service
L81: `receive` replaces the existing item instead of adding units; loses `on_hand` and resets `reserved` under live holds
L120: `record_loss` underflows `on_hand` and can leave `on_hand < reserved`
L47: `available()` underflows when `reserved > on_hand`; panics or allows over-reservation
L112: `ship` can underflow `on_hand` when `on_hand < reserved`
L157: `deltas` indexes `prices[i + 1]` out of bounds on the last iteration (always panics for non-empty input)
L127: `total_value` multiplication and sum can overflow `u64`
L204: `name.len() as u8` truncates names >255 bytes, producing corrupt records
L253: `Instant + ttl` panics on overflow while both locks are held, leaking the reservation and poisoning both mutexes