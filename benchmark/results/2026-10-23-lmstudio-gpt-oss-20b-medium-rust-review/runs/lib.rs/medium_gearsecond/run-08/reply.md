The module compiles, but several logic bugs, potential panics, and undefined‑behaviour
paths exist that could surface in real use or under test conditions.

### 1. Unsound subtraction

| Line | Problem | Why it matters |
|------|---------|----------------|
| **47** | `self.on_hand - self.reserved` | If `reserved > on_hand`, the subtraction underflows (wraps in release builds, panics in debug). This can happen after a buggy `record_loss` or manual data manipulation. |

### 2. Wrong semantics for receiving stock

| Line | Problem | Why it matters |
|------|---------|----------------|
| **80‑82** | `self.items.insert(sku, item);` replaces an existing SKU instead of adding to the current quantity. The comment says “for an existing SKU the units are added”, but the code drops name, price, and reservations. |

### 3. Potential underflow when recording loss

| Line | Problem | Why it matters |
|------|---------|----------------|
| **120** | `item.on_hand -= lost;` | If `lost > on_hand`, this underflows → panic in debug or silent wrap in release, corrupting inventory state. |

### 4. Off‑by‑one bug in `deltas`

| Lines | Problem | Why it matters |
|-------|---------|----------------|
| **156‑158** | Loop goes to `prices.len()`, then accesses `i+1`. The last iteration indexes out of bounds → panic at runtime. |

### 5. Unsafe unchecked indexing

| Line | Problem | Why it matters |
|------|---------|----------------|
| **185** | `unsafe { *self.slots.get_unchecked(slot) }` | Caller can pass an out‑of‑range index, causing UB and possible memory corruption. The API should return `Option<Sku>` or perform a bounds check. |

### 6. Unsafe pointer after potential reallocation

| Lines | Problem | Why it matters |
|-------|---------|----------------|
| **194‑196** | `let first = buf.as_ptr().wrapping_add(start);` then `buf.extend_from_slice(tail)` may reallocate, invalidating the raw pointer before it is dereferenced. This results in UB. |

### 7. Truncation of name length

| Line | Problem | Why it matters |
|------|---------|----------------|
| **204** | `name.len() as u8` | Names longer than 255 bytes overflow silently, producing an invalid encoded record that cannot be decoded correctly. |

### 8. Unsafe UTF‑8 conversion in decoder

| Line | Problem | Why it matters |
|------|---------|----------------|
| **218** | `std::str::from_utf8_unchecked` | If the incoming data contains non‑UTF‑8 bytes, this is undefined behaviour; a safe `from_utf8` check should be used. |

### 9. Concurrency ordering (minor)

The lock order in `place_hold`, `confirm`, and `sweep_expired` is consistent (`warehouse → holds → next_id` or vice versa), so deadlock is unlikely, but the current design still relies on sequential locking that could be simplified.

---

#### ISSUES:
L47: Unsound subtraction may underflow if reserved > on_hand  
L80‑82: receive() replaces existing SKU instead of adding quantity  
L120: record_loss() subtracts without saturating; can underflow  
L156‑158: deltas() loops out of bounds, panics  
L185: lookup() uses unchecked index, UB on out‑of‑range slot  
L194‑196: append_batch() dereferences pointer that may be invalid after reallocation  
L204: encode() truncates name length to u8 without validation  
L218: decode() uses from_utf8_unchecked; unsafe if bytes not valid UTF‑8  
L226–229 (Hold struct): typo `public qty` should be `pub qty` (compiles but confusing)  

These defects should be addressed before merging.