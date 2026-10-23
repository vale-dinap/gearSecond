Default arg `[]` built once at `def` time, one list object reused by every call. `append` mutates it, so state persists.

```python
def add(x, items=None):
    if items is None:
        items = []
    items.append(x)
    return items
```

`None` sentinel: fresh list per call when no arg passed. Same rule for `dict`, `set`, any mutable default.