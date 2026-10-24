**Underflow & Panic Risks**
`available()` (L47) subtracts `reserved` from `on_hand` without checking. If `reserved > on_hand`, it panics in debug builds or wraps to a huge number in release. `ship()` (L112) and `record_loss()` (L120) similarly subtract from `on_hand` without bounds checks, risking silent underflow.

**Logic & Specification Mismatches**
`receive()` (L80-81) uses `insert`, which overwrites an existing SKU. The doc comment (L78) states units should be added to the current `on_hand`. `deltas()` (L157) iterates `0..prices.len()` but accesses `prices[i + 1]`, causing an out-of-bounds panic on the last iteration. `total_value()` (L127) multiplies `u64` values without overflow protection; a large SKU count times a high price will wrap silently. `encode()` (L204) casts `name.len()` to `u8`, truncating names longer than 255 bytes.

**Memory Safety & UB**
`lookup()` (L185) uses `get_unchecked` to skip bounds validation on scanner input. Invalid slots trigger undefined behavior. `append_batch()` (L194) stores a raw pointer before `push` and `extend_from_slice`. Both may reallocate the `Vec`, invalidating the pointer. Dereferencing it at L196 is UB.

**Concurrency**
`place_hold()` acquires `warehouse` then `holds` (L245, L247). `confirm()` acquires `holds` then `warehouse` (L259, L265). Inconsistent lock ordering creates a deadlock risk under concurrent contention.

ISSUES:
L47: `on_hand - reserved` underflows when reserved exceeds stock
L80: `receive` overwrites existing SKU despite doc comment
L112: `on_hand -= qty` underflows if qty exceeds shelf stock
L120: `on_hand -= lost` underflows if loss exceeds shelf stock
L127: `on_hand * price_cents` can overflow u64
L157: `prices[i + 1]` panics when i == len-1
L185: `get_unchecked` skips bounds check, UB on invalid slot
L194: raw pointer stored before Vec may reallocate
L245/L259: inconsistent lock ordering between `place_hold` and `confirm`
L204: `name.len() as u8` truncates names longer than 255 bytes