**Cause:** default values evaluated once, at `def` time. `items=[]` makes one list object, stored on function (`add.__defaults__`). Every call without `items` reuses same list. First call appends 1, second appends 2 to same list -> `[1, 2]`.

**Fix:** use `None` sentinel, make new list inside:

```python
def add(x, items=None):
    if items is None:
        items = []
    items.append(x)
    return items
```

Now `add(1)` -> `[1]`, `add(2)` -> `[2]`.

Rule: never use mutable default (`[]`, `{}`, `set()`). Use `None`, build inside. Linters flag this (pylint `W0102`, ruff `B006`).