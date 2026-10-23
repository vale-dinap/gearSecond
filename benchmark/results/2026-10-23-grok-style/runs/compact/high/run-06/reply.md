The default `[]` is created once, when Python defines `add`, and every call that omits `items` reuses that same list. `add(1)` appends to it, so `add(2)` appends to the list that already holds `1`.

Use a new list on each call:

```python
def add(x, items=None):
    if items is None:
        items = []
    items.append(x)
    return items
```

`add(1)` returns `[1]`. `add(2)` returns `[2]`. Pass your own list when you want to keep appending: `add(3, items)`.