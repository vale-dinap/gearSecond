Default `[]` is built once, when Python defines `add`. Every call that omits `items` reuses that same list.

`add(1)` appends `1`. `add(2)` appends `2` onto the same list, so the result is `[1, 2]`.

Fix: default `None`, then make a new list inside the function.

```python
def add(x, items=None):
    if items is None:
        items = []
    items.append(x)
    return items
```

`add(1)` returns `[1]`. `add(2)` returns `[2]`. Pass your own list when you want to keep appending: `add(3, items)`.