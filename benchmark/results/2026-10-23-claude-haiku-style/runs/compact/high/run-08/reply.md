Default arg evaluated once, at `def` time. Same list object reused every call. `add(1)` appends to it, `add(2)` appends to same list, now `[1, 2]`.

Fix: use `None` sentinel, make new list per call.

```python
def add(x, items=None):
    if items is None:
        items = []
    items.append(x)
    return items
```

Now `add(1)` gives `[1]`, `add(2)` gives `[2]`.