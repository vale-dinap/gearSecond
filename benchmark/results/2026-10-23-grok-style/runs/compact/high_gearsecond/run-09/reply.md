The default `items=[]` is created once, when Python defines `add`, and every call that omits `items` reuses that same list. `add(1)` appends `1`, so the shared list is `[1]`. `add(2)` appends `2` to that same list and returns `[1, 2]`.

Fix: use `None` as the default and make a new list inside the function.

```python
def add(x, items=None):
    if items is None:
        items = []
    items.append(x)
    return items
```

Each call with no `items` now gets its own list. `add(1)` returns `[1]`. `add(2)` returns `[2]`. Pass a list when you want to keep appending to one you already have: `add(3, items)`.