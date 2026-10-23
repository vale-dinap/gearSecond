The default `items=[]` is created once, when Python defines `add`, not on each call. Every call with no `items` reuses that same list, so `add(1)` leaves `[1]` and `add(2)` appends to it and returns `[1, 2]`.

Fix: default to `None`, then make a new list inside the function.

```python
def add(x, items=None):
    if items is None:
        items = []
    items.append(x)
    return items
```

Now `add(1)` returns `[1]` and `add(2)` returns `[2]`. Pass your own list when you want to keep appending: `add(3, existing)`.