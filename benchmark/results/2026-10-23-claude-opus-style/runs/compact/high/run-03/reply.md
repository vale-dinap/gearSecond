Default args evaluated once, at `def` time. `items=[]` makes one list object, stored in `add.__defaults__`. Every call without `items` reuses same list → mutations persist across calls.

```python
add(1)  # [1]   — appends to shared default
add(2)  # [1, 2] — same list
add.__defaults__  # ([1, 2],)
```

Fix: use `None` sentinel, build fresh list inside body.

```python
def add(x, items=None):
    if items is None:
        items = []
    items.append(x)
    return items
```

Use `is None`, not `if not items` — else caller-passed empty list gets silently replaced instead of mutated.

Rule: never use mutable default (`[]`, `{}`, `set()`, custom objects). Linters flag it: pylint `W0102`, ruff/flake8-bugbear `B006`.