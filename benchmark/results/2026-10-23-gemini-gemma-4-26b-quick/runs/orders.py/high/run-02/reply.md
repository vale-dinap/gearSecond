The following defects were found in the `orders.py` module:

1.  **`page_count` Logic Error**: The function uses integer division (`//`). If `total_items` is not perfectly divisible by `per_page`, it will return one page fewer than required. For example, `page_count(10, 3)` returns `3` instead of `4`.
2.  **`add_tag` Mutable Default Argument**: The `tags=[]` parameter is a classic Python pitfall. The list is initialized once at definition time and shared across all subsequent calls to `add_tag` that do not provide a `tags` argument. This causes tags to accumulate across different orders, directly contradicting the docstring which states "tags are never shared between orders."
3.  **`average_total` Crash**: The docstring claims the function returns `0.0` when there are no orders. However, if `orders` is an empty list, `len(orders)` is `0`, leading to a `ZeroDivisionError`.
4.  **`in_window` Docstring Contradiction**: The docstring states the range is "both ends inclusive," but the implementation uses `day < end`. This makes the `end` date exclusive.
5.  **`recent_orders` Logic Error**: The condition `(today - o["day"]).days <= days` will evaluate to `True` for any date in the future (where the delta is negative). This means orders with dates ahead of `today` will be included in the "recent" list.

ISSUES:
L7: page_count returns incorrect number of pages when total_items is not divisible by per_page
L10: add_tag uses a mutable default argument which causes tags to be shared between orders
L19: average_total raises ZeroDivisionError instead of returning 0.0 when orders is empty
L24: in_window excludes the end date, contradicting the "inclusive" docstring
L36: recent_orders includes future dates because negative date deltas satisfy the condition