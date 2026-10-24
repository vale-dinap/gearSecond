The module contains a handful of logic bugs that will surface at runtime or produce incorrect results, contradicting the documented behaviour.

**Key problems**

| Function | Where | What is wrong |
|----------|-------|---------------|
| `page_count` | Line 7 (`return total_items // per_page`) | Uses floor division. It does **not** add an extra page when there’s a remainder (e.g., 10 items, 3 per page → should be 4 but returns 3). It also doesn’t guard against `per_page == 0`. |
| `add_tag` | Line 10 (`def add_tag(order, tag, tags=[]):`) and Line 12 (`tags.append(tag)`) | The default argument `tags=[]` is a mutable list that will be shared across all calls. This violates the docstring “tags are never shared between orders.” |
| `average_total` | Line 19 (`return sum(o["total"] for o in orders) / len(orders)`) | If `orders` is empty, division by zero raises an exception; the docstring says it should return `0.0`. |
| `in_window` | Line 24 (`return start <= day < end`) | The comparison excludes `end`; the docstring states both ends are inclusive `[start, end]`. |
| `recent_orders` | Line 36 (`picked = [o for o in orders if (today - o["day"]).days <= days]`) | Orders dated **after** today will have a negative difference and still satisfy the condition. The function should only include orders whose dates lie between today‑`days` and today, inclusive. |

---

### ISSUES:
L7: `page_count` uses floor division; fails to round up for non‑divisible totals.  
L10: mutable default argument causes tags to be shared across orders.  
L19: `average_total` crashes on empty list instead of returning 0.0.  
L24: `in_window` excludes the end date despite docstring saying inclusive.  
L36: `recent_orders` incorrectly includes future dates; missing lower‑bound check.