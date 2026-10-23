Default evaluated once, at `def` time. Same list object reused every call. `add(1)` mutates it → `[1]`; `add(2)` appends to same list → `[1, 2]`.

Check: `add.__defaults__` shows `([1, 2],)` after both calls.

Fix: use `None` sentinel, make new list inside.

```python
def add(x, items=None):
    if items is None:
        items = []
    items.append(x)
    return items
```

Now `add(1)` → `[1]`, `add(2)` → `[2]`. Same rule for any mutable default (`{}`, `set()`, objects).