Default `[]` is built once, when `def` runs, not per call. Both calls get the same list object, so `add(2)` appends to the list left by `add(1)`.

Fix: use `None` as sentinel, make new list per call.

```python
def add(x, items=None):
    if items is None:
        items = []
    items.append(x)
    return items
```

Now `add(1)` returns `[1]`, `add(2)` returns `[2]`.

Same bug hits `dict`, `set`, any mutable default. Immutable defaults (`int`, `str`, `tuple`, `None`) are safe.