Default `[]` evaluated once, at `def` time, so every call shares one list object. `append` mutates it, so `add(2)` sees `[1]` from before and returns `[1, 2]`.

Fix: use `None` sentinel, make fresh list per call.

```python
def add(x, items=None):
    if items is None:
        items = []
    items.append(x)
    return items
```

Check:

```python
add(1)  # [1]
add(2)  # [2]
```

Same applies to `{}`, `set()`, other mutable defaults.