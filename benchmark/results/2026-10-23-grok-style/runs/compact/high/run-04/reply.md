Default `[]` is created once, when Python defines `add`. Every call that skips `items` reuses that same list. First `add(1)` appends `1`. Second `add(2)` appends `2` onto the same object, so you get `[1, 2]`.

Fix: default to `None`, then make a fresh list inside the function.

```python
def add(x, items=None):
    if items is None:
        items = []
    items.append(x)
    return items
```

`add(1)` returns `[1]`. `add(2)` returns `[2]`. Pass your own list when you want to keep appending: `add(3, existing)`.