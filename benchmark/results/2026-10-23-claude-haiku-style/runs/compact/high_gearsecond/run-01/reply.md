Default `[]` is built once, when `def` runs, not per call. Every call that omits `items` gets that same list object, so `append` mutates it. `add(1)` adds 1, then `add(2)` appends 2 to that same list: `[1, 2]`.

Fix: use `None` as sentinel, create new list per call.

```python
def add(x, items=None):
    if items is None:
        items = []
    items.append(x)
    return items
```

Now `add(1)` returns `[1]`, `add(2)` returns `[2]`.