Default `items=[]` is created once, when Python defines `add`, and every call that omits `items` reuses that same list. `add(1)` appends `1` to it. `add(2)` appends `2` to that same list, so you get `[1, 2]`.

Make a new list on each call:

```python
def add(x, items=None):
    if items is None:
        items = []
    items.append(x)
    return items
```

`None` is immutable, so it is safe as a default. The `[]` inside the function runs every call, so `add(1)` returns `[1]` and `add(2)` returns `[2]`. Pass your own list when you want to keep appending to it: `add(3, items)`.