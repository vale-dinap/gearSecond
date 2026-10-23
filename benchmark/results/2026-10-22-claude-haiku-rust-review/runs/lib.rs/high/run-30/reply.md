I reviewed this by reading the code. I haven't compiled it or run the tests. Several items are real soundness problems, so I'd block the merge on them.

**Undefined behaviour and memory safety**

- **`lookup` (L185):** `get_unchecked` takes a slot number from scanner messages. Any `slot >= len` is an out-of-bounds read. The "hot path" comment doesn't justify it, since `self.slots.get(slot).copied().flatten()` is essentially free and returns `None` for bad input.
- **`append_batch` (L194–196):** `first` is a raw pointer taken before `extend_from_slice`, which can reallocate `buf`. Dereferencing `first` afterwards reads freed memory. The head value is already in scope as `head`, so no `unsafe` is needed.
- **`decode` (L218):** `from_utf8_unchecked` runs on bytes from the network. Invalid UTF-8 produces an invalid `String`, which is UB. Use `std::str::from_utf8` and return `Malformed`.

**Panics and integer overflow**

- **`deltas` (L157):** the loop runs `0..prices.len()`, so the last iteration reads `prices[len]`. Every non-empty input panics. Use `prices.windows(2)`. The `i64` subtraction can also overflow for extreme values.
- **`record_loss` (L120):** `on_hand -= lost` has no bounds check. It panics in debug and wraps in release, which produces huge phantom stock. It also ignores `reserved`, so `on_hand` can fall below `reserved`.
- **`available` (L47):** `on_hand - reserved` assumes `on_hand >= reserved`, and `record_loss` breaks that. In release, the wrapped result makes `reserve` (L91–92) see a huge `have` and allow over-reservation. `low_stock` is affected the same way.
- **`total_value` (L127):** `on_hand as u64 * price_cents` and the `sum` can overflow `u64` for large stock at high prices. Use `checked_*` or `u128`.
- **`place_hold` (L253):** `Instant::now() + ttl` panics on a large `ttl`. This happens after `reserve` (L246) has succeeded, so the reservation leaks and both mutexes are poisoned.

**Logic errors**

- **`receive` (L81):** `HashMap::insert` replaces the existing item. Receiving more of a known SKU resets `on_hand` to `qty`, zeroes `reserved`, and overwrites name and price. The doc says units are added. If holds are outstanding, a later `ship` does `reserved -= qty` on a zero, which underflows. `Service` doesn't currently call `receive`, so this is latent through the service path, but it's the `Warehouse` contract.
- **`encode` (L204):** `name.len() as u8` silently truncates names over 255 bytes, but all the name bytes are still written. The frame is corrupt and decodes to garbage. Return an error instead.
- **`decode` (L215):** trailing bytes are accepted silently. A buffer holding two records, or junk after one, returns only the first with no error. Check `rest.len() == len + 8` if the contract is one record per call.
- **`place_hold` (L246):** expired holds keep their units reserved until `sweep_expired` runs, and nothing in this module schedules it. `reserve` doesn't consider expiry, so stock can be refused while the holds blocking it are already dead. Sweep, or check expiry inside the availability check.

**Concurrency**

- **Lock-order inversion (L259 vs L245/247 and L272/273):** `confirm` locks `holds` then `warehouse`. `place_hold` and `sweep_expired` lock `warehouse` then `holds`. A `confirm` racing with either can deadlock. Use one lock order everywhere, or put `warehouse`, `holds` and `next_id` behind one `Mutex`, since they form one state machine.
- **Poisoning:** every `lock().unwrap()` turns a single panic into permanent failure of the service. Combined with the panics above, one bad input can take the service down. Fix the panic sources, and consider recovering from poisoned locks.

Not counted above: `log` (L69, L82) grows without bound in a long-running service. The tests also don't exercise any of these paths. `deltas` would panic on first use, and nothing covers `record_loss`, non-UTF-8 input, long names, or concurrent `confirm`/`place_hold`. Running `cargo miri test` would confirm the UB findings.

ISSUES:
L47: available() underflows when reserved > on_hand, which record_loss can cause
L81: receive() replaces the existing item instead of adding stock, resetting reserved to 0
L120: record_loss() subtracts without a bounds check (panics or wraps) and ignores reserved
L127: total_value() multiplication and sum can overflow u64
L157: deltas() reads prices[len] on the last iteration, panicking on any non-empty input; i64 subtraction can overflow
L185: lookup() uses get_unchecked on an untrusted slot index, an out-of-bounds read (UB)
L196: append_batch() dereferences a pointer taken before extend_from_slice, which may reallocate (use-after-free)
L204: encode() truncates the name length to u8 for names over 255 bytes, corrupting the frame
L215: decode() accepts trailing bytes without error
L218: decode() calls from_utf8_unchecked on network bytes, which is UB on invalid UTF-8
L246: place_hold() treats expired-but-unswept holds as still reserved, refusing stock unnecessarily
L253: place_hold() panics on a large ttl after the reservation is made, leaking it and poisoning the mutexes
L259: confirm() locks holds then warehouse, the opposite of place_hold/sweep_expired, so the two can deadlock