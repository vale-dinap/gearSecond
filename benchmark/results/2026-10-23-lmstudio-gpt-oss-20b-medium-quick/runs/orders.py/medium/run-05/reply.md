**Review of `orders.py`**

The module contains several functions that are meant to be straightforward helpers for a shop backend.  
Below are the concrete defects that violate the documented behaviour or would cause runtime errors in real use.

| Function | Issue | Why it’s wrong |
|----------|-------|----------------|
| `page_count` (lines 5‑7) | Uses floor division (`//`) and doesn’t add an extra page when there is a remainder. Also does not guard against `per_page == 0`. | The docstring says “Number of pages needed” – for 10 items with 3 per page you need **4** pages, but the current code returns 3. A zero‑division error would also surface if `per_page` were 0. |
| `add_tag` (lines 10‑14) | The default argument `tags=[]` is a mutable object that will be shared across calls; existing tags on an order are overwritten instead of appended to. | Docstring: “tags are never shared between orders.” The current implementation violates this and can lead to subtle bugs where multiple orders end up sharing the same tag list. |
| `average_total` (lines 17‑19) | Divides by `len(orders)` without checking for an empty list, raising a `ZeroDivisionError`. | Docstring explicitly says “0.0 when there are no orders.” |
| `in_window` (lines 22‑24) | Uses `< end`, making the upper bound exclusive; the docstring requests inclusive bounds `[start, end]`. | For a window from Jan 1 to Jan 10, a day on Jan 10 should return True but currently returns False. |
| `recent_orders` (lines 34‑37) | Includes orders whose date is in the future because `(today - o["day"]).days` can be negative and still satisfy `<= days`. | The intent is “Orders placed within the last `days` days,” so future dates must be excluded. |

No style issues were flagged, as requested.

---

### ISSUES:
```
L5: page_count uses floor division; fails when total_items not divisible by per_page.
L10: add_tag default mutable list leads to shared tags across orders.
L17: average_total does not handle empty order lists; raises ZeroDivisionError.
L22: in_window upper bound is exclusive, contradicting inclusive docstring.
L34: recent_orders includes future dates due to negative day differences.
```