The default `[]` is created once, when Python defines `add`. Every call that omits `items` reuses that same list, so `add(1)` leaves `[1]` in it and `add(2)` appends to that and returns `[1, 2]`.

Use `None` as the default and make a new list inside the function:

```python
def add(x, items=None):
    if items is None:
        items = []
    items.append(x)
    return items
```

Then `add(1)` returns `[1]` and `add(2)` returns `[2]`. Pass your own list when you want to keep adding to it: `add(2, items)`.