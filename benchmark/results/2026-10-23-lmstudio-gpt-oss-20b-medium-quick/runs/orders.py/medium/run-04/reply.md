**Review**

| Function | Problem | Why it matters |
|----------|---------|----------------|
| `page_count` | Uses floor division (`//`). It does not round up when there is a remainder, so it under‑reports the number of pages (e.g., 10 items with 3 per page → 3 instead of 4). It also doesn’t guard against `per_page == 0`, which would raise a `ZeroDivisionError`. | The docstring promises “Number of pages needed …”, implying that any leftover items should trigger an additional page. |
| `add_tag` | Default argument `tags=[]` is mutable and shared across calls, so tags added to one order will appear in all subsequent orders that use the default list. Moreover, it assigns this shared list back into the order (`order["tags"] = tags`). | The docstring explicitly states *“tags are never shared between orders.”* |
| `average_total` | Divides by `len(orders)` without checking for an empty list, causing a `ZeroDivisionError`. The docstring says it should return `0.0` when there are no orders. | This crashes the application on an otherwise valid input (an empty order list). |
| `in_window` | Implements `[start, end)` instead of `[start, end]`; the end date is excluded despite the inclusive description in the docstring. | Users expecting the last day to be counted will receive incorrect results. |
| `recent_orders` | Filters with `(today - o["day"]).days <= days`, which also accepts dates **after** today (negative differences) and does not enforce that orders are within the past `days`. | Future‑dated orders would appear in the “last N days” list, contradicting the docstring. |

---

### ISSUES

```
L7: page_count returns floor division; fails to round up when there is a remainder.
L10-L14: add_tag uses mutable default argument and shares tags between orders.
L19: average_total divides by len(orders) without handling empty list → ZeroDivisionError.
L24: in_window excludes the end date; should be <= end for inclusive range.
L36: recent_orders includes future dates; does not restrict to past days only.
```
