**Cause:** default args evaluated once, at `def` time. `items=[]` makes one list object, stored on function (`add.__defaults__`). Every call without `items` reuses same list. First call appends 1 → `[1]`. Second call appends 2 to same list → `[1, 2]`.

**Fix:** use `None` sentinel, make new list inside:

```python
def add(x, items=None):
    if items is None:
        items = []
    items.append(x)
    return items
```

Now `add(1)` → `[1]`, `add(2)` → `[2]`.

Same trap for any mutable default: `{}`, `set()`, custom objects. Linters flag it (pylint `W0102`, ruff `B006`).