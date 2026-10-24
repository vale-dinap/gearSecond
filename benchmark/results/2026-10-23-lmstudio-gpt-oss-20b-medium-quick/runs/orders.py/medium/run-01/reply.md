The module contains several logical bugs that will cause incorrect results or runtime crashes, especially when used in production.

### Detailed Problems

1. **`page_count`**  
   - The function returns `total_items // per_page`, which truncates the division and therefore under‑reports the number of pages when there is a remainder (e.g., 10 items with 3 per page should need 4 pages, but the code returns 3).  
   - It also silently fails with a `ZeroDivisionError` if `per_page` is zero. The docstring says “Number of pages needed”, so the function should compute the ceiling of the division and validate the arguments.

2. **`add_tag`**  
   - Uses a mutable default argument (`tags=[]`). Subsequent calls will share the same list, so tags added for one order may appear on another, contradicting the docstring that tags are never shared between orders.  
   - The function mutates the passed `order` dict in place; callers might not expect this side‑effect.

3. **`average_total`**  
   - When `orders` is empty it performs division by zero, raising a `ZeroDivisionError`. The docstring explicitly states that the result should be `0.0` for an empty list.

4. **`in_window`**  
   - Implements `[start, end)` rather than `[start, end]`. It returns `False` when `day == end`, which violates the inclusive specification in the docstring.

5. **`recent_orders`**  
   - Includes orders dated *after* `today` because `(today - o["day"]).days` is negative and still ≤ `days`. The function should ignore future dates.  
   - It does not enforce that the difference be non‑negative, so future orders are mistakenly considered “within the last N days”.

---

## ISSUES:
```
L7: Uses floor division; fails to round up for incomplete pages.
L10: Mutable default argument causes tags to be shared across orders.
L19: Division by zero when order list is empty; should return 0.0 per docstring.
L24: Exclusive end bound contradicts inclusive window described in docstring.
L36: Includes future‑dated orders and accepts negative day differences, violating “last N days”.
```
