I read the module without compiling or running it. The most serious problems are an out-of-bounds `deltas` call that panics on every non-empty input, two unsafe blocks that read untrusted input or dangling memory, and a lock-order inversion that can deadlock the service.

**Undefined behaviour and memory safety**

- **`decode`, `src/lib.rs:218`:** `from_utf8_unchecked` runs on bytes from the network. Invalid UTF-8 inside a `String` is undefined behaviour, and the input is attacker-controlled. Use `std::str::from_utf8` and return `InvError::Malformed` on failure.
- **`SlotTable::lookup`, `src/lib.rs:185`:** `get_unchecked` is called with `slot` from a scanner message, so any out-of-range value is an out-of-bounds read. The "hot path" comment does not justify it: `self.slots.get(slot).copied().flatten()` is just as cheap and returns `None` correctly.
- **`append_batch`, `src/lib.rs:193-196`:** `first` is taken from `buf.as_ptr()` before `extend_from_slice`. If the extend reallocates the buffer, which happens whenever the tail does not fit in the spare capacity, `*first` is a use-after-free. The unsafe block is also unnecessary: the first SKU is simply `head`, so `Some((head, buf.len()))` is correct.

**Panics and arithmetic**

- **`deltas`, `src/lib.rs:156-157`:** The loop runs `i` over `0..prices.len()` and reads `prices[i + 1]`. On the last iteration that is `prices[len]`, so the function panics for every non-empty input. The loop should run over `0..prices.len() - 1`, or use `prices.windows(2)`. The capacity computation on line 155 already assumes that range. The subtraction can also overflow `i64` for extreme prices, so `checked_sub` or a documented wrapping behaviour would be safer.
- **`Item::available`, `src/lib.rs:47`:** This is `on_hand - reserved` on `u32`. `record_loss` (line 120) can reduce `on_hand` below `reserved`, which makes `available()` underflow. In debug builds that panics, and in release it wraps to a huge number, so `reserve` would accept almost any quantity. `low_stock` (line 132) and `reserve` (line 91) both depend on it.
- **`ship`, `src/lib.rs:111-112`:** The guard checks `qty <= reserved` but not `qty <= on_hand`. After a loss, `on_hand -= qty` underflows the same way. Inside `Service::confirm`, that panic happens while the mutexes are held, which poisons them. Every later `.lock().unwrap()` then panics, so one bad shipment takes down the whole service.
- **`record_loss`, `src/lib.rs:120`:** There is no check that `lost <= on_hand`, so this underflows directly. It should return an error or clamp, and it should decide what happens to reservations when the loss is larger than the unreserved stock.
- **`release`, `src/lib.rs:101`:** `saturating_sub` silently accepts releases larger than the reservation, which hides exactly the invariant violations above. Returning an error would make them visible.
- **`total_value`, `src/lib.rs:127`:** `on_hand as u64 * price_cents` and the `u64` sum can overflow for large prices. Use `checked_mul` and `checked_add`, or saturate with a documented limit.
- **`place_hold`, `src/lib.rs:253`:** `Instant::now() + ttl` panics if `ttl` is very large. Use `checked_add` and return an error.

**Logic errors**

- **`receive`, `src/lib.rs:81`:** The doc comment says units are added to an existing SKU, but `insert` replaces the whole item. That resets `reserved` to 0 while holds still refer to those units, so a later `confirm` underflows in `ship` (lines 111-112). Fix it by updating the existing entry, adding `qty` to `on_hand`, and only setting name and price for new SKUs.
- **`encode`, `src/lib.rs:204`:** `name.len() as u8` silently truncates names longer than 255 bytes, but the full name is still written. The decoder then reads the wrong fields. Reject names over 255 bytes, or truncate on a character boundary and keep the length consistent with what is written.
- **`confirm`, `src/lib.rs:260-266`:** The hold is removed from the map before `ship` runs. If `ship` fails, the reservation is never released and the units stay locked permanently.

**Concurrency**

- **Lock-order inversion, `src/lib.rs:245-247`, `259-265`, `272-273`:** `place_hold` and `sweep_expired` take `warehouse` and then `holds`. `confirm` takes `holds` and then `warehouse`. If one thread is in `place_hold` holding `warehouse` while another is in `confirm` holding `holds`, both wait forever. Pick one order and use it everywhere. Taking `warehouse` first in `confirm` is the smallest change.

ISSUES:
L47: `available()` underflows when reserved exceeds on_hand, which record_loss can cause; this panics in debug and over-reserves in release, and it also affects low_stock
L81: `receive` replaces an existing SKU, resetting reserved to 0 while holds still reference the units
L111: `ship` can underflow on_hand after a loss; the panic happens while locks are held and poisons the service mutexes
L120: `record_loss` subtracts without checking, so on_hand underflows
L127: `total_value` can overflow in the u64 multiplication and sum
L157: `deltas` reads prices[len] on the last iteration, so it panics on every non-empty input
L157: `deltas` i64 subtraction can overflow for extreme prices
L185: `lookup` uses get_unchecked on an untrusted slot index, which is an out-of-bounds read
L194: `append_batch` reads through a pointer that is dangling after extend_from_slice reallocates
L204: `encode` truncates names longer than 255 bytes with `as u8` and writes a corrupt frame
L218: `decode` uses from_utf8_unchecked on untrusted network bytes, which is undefined behaviour for invalid UTF-8
L253: `place_hold` panics when `Instant::now() + ttl` overflows
L259: `confirm` locks holds then warehouse, the reverse of place_hold and sweep_expired, which can deadlock
L260: `confirm` removes the hold before ship succeeds, so a failed ship leaks the reservation permanently