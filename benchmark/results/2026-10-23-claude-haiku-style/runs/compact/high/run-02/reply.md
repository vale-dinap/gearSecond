Default arg evaluated once, at `def` time. Same list object reused every call, so `add(1)` mutates it and `add(2)` appends to that same list.

Fix: use `None` sentinel, make new list per call.

```python
def add(x, items=None):
    if items is None:
        items = []
    items.append(x)
    return items
```

Now `add(1)` -> `[1]`, `add(2)` -> `[2]`.

Only use `items=[]` intentionally if you want shared state across calls.