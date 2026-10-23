Default `[]` built once at `def` time, not per call. Every call that omits `items` gets the same list object, so `append` mutates it.

```python
def add(x, items=None):
    if items is None:
        items = []
    items.append(x)
    return items
```

`None` is immutable and a sentinel, so each call without `items` makes a fresh list. Same rule for `dict`, `set`, and other mutable defaults.