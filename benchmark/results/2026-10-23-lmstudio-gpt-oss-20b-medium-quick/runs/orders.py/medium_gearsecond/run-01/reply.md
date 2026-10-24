The module contains several logical bugs that would lead to incorrect results or runtime crashes, and some behaviours contradict the supplied docstrings.

**Key problems**

1. **`page_count` (line 5)**  
   - Uses floor division (`//`). For non‑multiples of `per_page`, the last page is omitted.  
   - Does not guard against `per_page == 0`; a zero value raises `ZeroDivisionError`.

2. **`add_tag` (line 10)**  
   - The default argument `tags=[]` is mutable and shared across calls, violating “tags are never shared between orders”.  
   - Modifies the list in‑place; subsequent calls that don’t supply an explicit list keep adding to the same list.

3. **`average_total` (line 17)**  
   - When `orders` is empty, `len(orders)` is zero → division by zero crash.  
   - Docstring says it should return `0.0` for no orders; this case isn’t handled.

4. **`in_window` (line 22)**  
   - Implements `[start, end)` instead of the inclusive `[start, end]` specified in the docstring. The `end` date is excluded.

5. **`recent_orders` (line 34)**  
   - Includes orders whose `day` is after `today`. `(today - future_day).days` is negative and still satisfies `<= days`, so future orders are incorrectly returned.  
   - Does not enforce that the difference is non‑negative, contrary to “within the last `days` days”.

Other functions (`apply_coupon`) behave as documented.

---

### ISSUES:
```
L5: page_count uses floor division; fails on non‑multiples and crashes when per_page==0
L10: add_tag default mutable list shares tags across orders
L17: average_total divides by zero for empty order list
L22: in_window excludes end date (should be inclusive)
L34: recent_orders includes future dates; no check for non‑negative delta
```