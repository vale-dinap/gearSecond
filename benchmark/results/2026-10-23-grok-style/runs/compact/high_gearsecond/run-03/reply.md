The default `items=[]` is created once, when Python defines `add`, and every call that omits `items` reuses that same list. The first `add(1)` appends `1` to it. The second `add(2)` appends `2` to the same list, so you get `[1, 2]`.

Fix: use `None` as the default and create a new list inside the function.

```python
def add(x, items=None):
    if items is None:
        items = []
    items.append(x)
    return items
```

Now `add(1)` returns `[1]` and `add(2)` returns `[2]`. Passing your own list still works: `add(3, [1, 2])` returns `[1, 2, 3]`.