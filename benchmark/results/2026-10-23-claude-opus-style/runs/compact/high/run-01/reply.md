Default args evaluated once, at `def` time, not per call. `items=[]` makes one list object, stored in `add.__defaults__`. Every call without `items` reuses same list. First call appends 1 → `[1]`. Second call appends 2 to same list → `[1, 2]`.

Check:
```python
add(1); print(add.__defaults__)  # ([1],)
```

Fix: use `None` sentinel, make new list inside body.

```python
def add(x, items=None):
    if items is None:
        items = []
    items.append(x)
    return items
```

Now `add(1)` → `[1]`, `add(2)` → `[2]`.

Use `is None`, not `if not items`. Otherwise caller passing own empty list gets it swapped for new one, and their list never mutated.

Same trap for any mutable default: `{}`, `set()`, custom objects. Linters flag it (pylint `W0102`, ruff/flake8-bugbear `B006`).