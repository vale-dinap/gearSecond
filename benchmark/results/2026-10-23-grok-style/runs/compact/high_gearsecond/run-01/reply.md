The default `[]` is created once, when Python defines `add`, and every call that omits `items` reuses that same list. `append` mutates it, so the first call leaves `[1]` and the second call appends `2` onto that same object.

Bind the default to `None` and make a new list inside the function:

```python
def add(x, items=None):
    if items is None:
        items = []
    items.append(x)
    return items
```

`add(1)` returns `[1]`. `add(2)` returns `[2]`. Pass your own list when you want to keep appending to it: `add(3, existing)`.