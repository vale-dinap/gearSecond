Default `[]` is built once, when `def` runs, not per call. Both calls share that one list, so `add(1)` appends to it and `add(2)` appends to the same list again: `[1, 2]`.

Fix: use `None` as sentinel, make new list inside.

```python
def add(x, items=None):
    if items is None:
        items = []
    items.append(x)
    return items
```

Now `add(1)` returns `[1]`, `add(2)` returns `[2]`.

Same bug hits `dict`, `set`, any mutable default.