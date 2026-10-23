The default `[]` is created once, when Python defines `add`, and every call that omits `items` reuses that same list. `add(1)` appends `1` to it. `add(2)` appends `2` to the same object, so you get `[1, 2]`.

Use `None` as the default and make a new list inside the function:

```python
def add(x, items=None):
    if items is None:
        items = []
    items.append(x)
    return items
```

Then `add(1)` returns `[1]` and `add(2)` returns `[2]`. Pass your own list when you want to keep appending to it.