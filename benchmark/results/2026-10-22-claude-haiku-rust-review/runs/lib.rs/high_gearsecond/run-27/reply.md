## Review of `src/lib.rs`

The most serious problems are undefined behaviour from `unsafe` code on untrusted or stale data, and a lock-ordering deadlock in `Service`.

**Undefined behaviour**

- **`SlotTable::lookup` (L185):** `get_unchecked` runs on a slot number that comes from a scanner message. An out-of-range slot reads past the end of the allocation. Use `self.slots.get(slot).copied().flatten()`. The "hot path" comment doesn't justify removing the check.
- **`append_batch` (L193–196):** `first` is a pointer into `buf` taken before `extend_from_slice`. If the extend reallocates, `first` dangles and `*first` is a use-after-free. Read `buf[start]` or simply return `head`.
- **`decode` (L218):** `from_utf8_unchecked` runs on bytes received from the network. Invalid UTF-8 produces a `String` that violates its invariant, which is UB. Use `std::str::from_utf8` and map the error to `InvError::Malformed`.

**Concurrency**

- **Lock-order inversion (L245–247, L259–265, L272–273):** `place_hold` and `sweep_expired` take `warehouse` then `holds`. `confirm` takes `holds` then `warehouse` (L262 and L265). Two threads running `confirm` and `place_hold` can deadlock. Pick one order everywhere, or put the warehouse and holds behind one mutex.
- **Leaked reservation (L260–266):** `confirm` removes the hold before calling `ship`. If `ship` returns `Insufficient`, the hold is gone and its units stay reserved forever. Ship first and remove the hold only on success, or re-insert it on error.

**Logic and invariant errors**

- **`receive` overwrites stock (L80–81):** `insert` replaces an existing item and zeroes `on_hand` and `reserved`. The doc says units are added. Outstanding holds are also orphaned, so `available()` over-counts. Use `entry(sku)` and add `qty` to `on_hand` when the SKU exists.
- **`record_loss` breaks the invariant (L120):** Nothing stops `on_hand` from dropping below `reserved`. `on_hand -= lost` can also underflow and panic in debug builds or wrap in release builds. Check `lost <= on_hand - reserved`, or the invariant that `reserved <= on_hand`, and return an error.
- **Unchecked subtraction in `available` (L47) and `ship` (L112):** Both assume `reserved <= on_hand`. Once `record_loss` breaks that, `available()` underflows and `ship` panics. Make these checked or enforce the invariant.
- **`encode` truncates names (L204):** `name.len() as u8` wraps for names over 255 bytes. The frame then has a wrong length prefix and corrupt content. Reject names over 255 bytes with an error.
- **Overflow in `total_value` (L127):** `on_hand as u64 * price_cents` and the sum can overflow `u64` and panic in debug builds. Use `checked_mul`/`checked_add` or `saturating_*`.
- **Overflow in `deltas` (L157):** `prices[i+1] - prices[i]` can overflow `i64` for extreme inputs. Use `checked_sub` or document the range.
- **Panic on large TTL (L253):** `Instant::now() + ttl` panics when `ttl` is very large. Use `checked_add` and return an error.

No issues found in `moving_average` (an empty result when `window > len` is correct), in `reserve`, or in the `try_into().unwrap()` calls in `decode`, since the length checks make them infallible.

ISSUES:

L185: `get_unchecked` with untrusted slot index, out-of-bounds read (UB)

L194: `first` pointer taken before `extend_from_slice`, dangling after reallocation (UB)

L218: `from_utf8_unchecked` on network input, invalid UTF-8 in `String` (UB)

L245: `place_hold` locks warehouse then holds, opposite order to `confirm`, deadlock

L262: `confirm` takes warehouse lock while holding holds lock, lock-order inversion, deadlock

L266: `confirm` removes hold before `ship`, failed ship leaks reservation permanently

L80: `receive` replaces existing item, zeroing on_hand and reserved, contradicts doc

L120: `record_loss` underflows `on_hand` and can drop it below `reserved`

L112: `ship` underflows `on_hand` once `reserved <= on_hand` invariant is broken

L47: `available()` underflows when `reserved > on_hand`

L204: `name.len() as u8` truncates names over 255 bytes, corrupt wire frame

L127: `total_value` multiplication and sum can overflow u64

L157: `deltas` i64 subtraction can overflow

L253: `Instant::now() + ttl` panics on very large TTL