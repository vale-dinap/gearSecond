**Why:** Default value evaluated once, at `def` time, not per call. Same list object reused every call. First call appends 1 → `[1]`. Second call appends 2 to *same* list → `[1, 2]`.

Proof:
```python
add.__defaults__  # ([1, 2],) after two calls
```

**Fix:** use `None` sentinel, make new list inside body.
```python
def add(x, items=None):
    if items is None:
        items = []
    items.append(x)
    return items
```

Now `add(1)` → `[1]`, `add(2)` → `[2]`. Passing own list still works: `add(3, mylist)`.

Rule: never use mutable default (`[]`, `{}`, `set()`, objects). Use `None` + create inside. Linters flag this (ruff `B006`, pylint `W0102`).