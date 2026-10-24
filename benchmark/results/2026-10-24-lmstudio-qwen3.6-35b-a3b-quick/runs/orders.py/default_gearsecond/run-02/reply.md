`page_count` uses floor division (`//`). Returns 3 for 10 items / 3 per page instead of 4. Also crashes on `per_page=0`.

`add_tag` uses a mutable default `tags=[]`. The list persists across calls, sharing state between orders and violating the docstring guarantee.

`average_total` divides by `len(orders)` without an emptiness check. Raises `ZeroDivisionError` on `[]` instead of returning `0.0` as documented.

`in_window` uses `< end`. Excludes the end date, contradicting the inclusive `[start, end]` docstring.

`recent_orders` only checks `(today - o["day"]).days <= days`. Negative differences (future dates) pass the check, incorrectly including future orders.

ISSUES:
L7: Floor division undercounts pages for non-multiples; crashes on zero divisor.
L10: Mutable default `tags=[]` shares state across calls.
L19: Divides by `len(orders)` without empty check; crashes instead of returning `0.0`.
L24: Exclusive upper bound `< end` contradicts inclusive docstring.
L36: Lacks lower bound check; includes future orders.