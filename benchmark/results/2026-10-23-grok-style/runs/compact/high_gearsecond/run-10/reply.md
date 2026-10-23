The default `[]` is created once, when Python defines `add`, and every call that omits `items` reuses that same list. `add(1)` appends `1` to it. `add(2)` appends `2` to the same object, so the result is `[1, 2]`.

Create a new list on each call:

```python
def add(x, items=None):
    if items is None:
        items = []
    items.append(x)
    return items
```

`None` is immutable, so the default is safe. The `if` builds a fresh list only when the caller does not pass one.