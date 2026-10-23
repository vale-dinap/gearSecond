## Summary

The module has several definite defects. Two are undefined behaviour on untrusted input (`lookup` and `decode`), and `append_batch` has a dangling-pointer read. `deltas` panics on every non-empty input. `receive` corrupts stock accounting, and `place_hold`/`confirm` can deadlock. The existing tests exercise none of these paths.

## Undefined behaviour

- **`SlotTable::lookup` (L183–186).** `slot` comes from a scanner message, and `get_unchecked` with an out-of-range index is an out-of-bounds read. The "hot path" justification doesn't hold up: the function already returns `Option`, and the bounds check is trivial. Use `self.slots.get(slot).copied().flatten()`.
- **`append_batch` (L190–198).** `first` points at the head element. `extend_from_slice` can reallocate `buf`, and then `*first` reads freed memory. The unsafe block is also unnecessary, since the returned value is just `head`:
  ```rust
  pub fn append_batch(buf: &mut Vec<Sku>, batch: &[Sku]) -> Option<(Sku, usize)> {
      let (&head, tail) = batch.split_first()?;
      buf.push(head);
      buf.extend_from_slice(tail);
      Some((head, buf.len()))
  }
  ```
- **`decode` (L218).** `from_utf8_unchecked` runs on network bytes. Invalid UTF-8 produces an invalid `String`, which is UB. Use `std::str::from_utf8(&rest[..len]).map_err(|_| InvError::Malformed("name is not UTF-8"))?`.

## Panics and arithmetic

- **`deltas` (L156–158).** The loop runs `i` over `0..prices.len()` and indexes `prices[i + 1]`, so the last iteration reads `prices[len]`. Any non-empty input panics. Use `prices.windows(2).map(|w| w[1] - w[0]).collect()`. The subtraction can still overflow `i64` for extreme values, so use `checked_sub` or `i128` if that matters.
- **`record_loss` (L120).** `lost` is not checked against `on_hand`, so the subtraction underflows. It also ignores reservations, so `on_hand` can drop below `reserved`. That breaks the invariant `available()` relies on.
- **`Item::available` (L47).** `on_hand - reserved` underflows once the invariant above is broken. Fix the invariant in `record_loss` (reject losses above `available()`). Don't paper over it with `saturating_sub`.
- **`total_value` (L127).** `on_hand as u64 * price_cents` and the `u64` sum can both overflow for large prices. Use `u128` and widen the return type, or use checked arithmetic.
- **`place_hold` (L253).** `Instant::now() + ttl` panics when `ttl` is very large (e.g. `Duration::MAX`). Use `checked_add` and return an error. Do this before `reserve` (L246), otherwise a failed hold leaves stock reserved.

## Concurrency

- **Lock-order inversion.** `place_hold` (L245 → L247) and `sweep_expired` (L272 → L273) take `warehouse` then `holds`. `confirm` (L259 → L262/L265) takes `holds` then `warehouse`. If one thread is in `place_hold` holding `warehouse` and another is in `confirm` holding `holds`, both wait forever. Take `warehouse` first in `confirm` as well:
  ```rust
  let mut wh = self.warehouse.lock().unwrap();
  let mut holds = self.holds.lock().unwrap();
  ```
- **Mutex poisoning.** Every call uses `.lock().unwrap()`. One panic while a guard is held (for example the overflows above) poisons the mutex, and every later call then panics too. That turns a single bad request into a service outage.

## Data corruption and logic

- **`receive` (L80–81).** The doc says units are added to existing stock, but `insert` replaces the whole `Item`. Effects:
  - `on_hand` becomes `qty`, discarding existing stock.
  - `reserved` resets to 0 while holds are still outstanding, so the same units can be reserved twice.
  - An outstanding hold's `ship` can consume units that another hold reserved.
  - Name and price are silently overwritten.

  Use `entry(sku)`, create the item only if missing, and add to `on_hand` with a checked add.
- **`encode` (L204).** `name.len() as u8` silently truncates names over 255 bytes. The length prefix then disagrees with the payload, and `decode` reads the SKU and quantity from the wrong offsets. Return `Result` and reject long names.

## Lesser concerns (not counted as defects above)

- `release` (L101) uses `saturating_sub`, which hides over-release and accounting bugs.
- `log` (L69 and the `push` calls) grows without bound in a long-running service.
- Nothing in the module calls `sweep_expired`, and `reserve` does not sweep. Expired holds keep blocking stock until something external sweeps.
- `moving_average` (L144) panics on `window == 0`. The doc comment doesn't mention it.
- The tests don't cover any of the defects. Worth adding: `deltas` on a one-element slice, `receive` twice on the same SKU, `record_loss` above on-hand, names over 255 bytes, invalid UTF-8 in `decode`, out-of-range `lookup`, and a concurrent `place_hold`/`confirm` stress test.

ISSUES:
L47: `available()` underflows when reserved exceeds on_hand (panic in debug, wraps in release)
L80: `receive` replaces the existing item instead of adding units; resets reserved to 0 while holds are outstanding
L120: `record_loss` subtracts without checking on_hand (underflow) and ignores reservations
L127: `total_value` u64 multiplication and sum can overflow
L157: `deltas` indexes prices[len] and panics on any non-empty input
L185: `lookup` uses get_unchecked on an untrusted slot index (out-of-bounds read, UB)
L196: `append_batch` dereferences a pointer that extend_from_slice can invalidate by reallocating (UB)
L204: `encode` truncates name length to u8, producing corrupt records for names over 255 bytes
L218: `decode` uses from_utf8_unchecked on untrusted bytes (UB on invalid UTF-8)
L253: `place_hold` computes Instant + Duration without checking overflow (panics on large TTL)
L259: `confirm` takes holds before warehouse, inverting the order used by place_hold and sweep_expired (deadlock)