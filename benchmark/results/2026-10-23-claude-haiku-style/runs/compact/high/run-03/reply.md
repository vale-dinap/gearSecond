Default `[]` is built once, when `def` runs. Every call without `items` reuses that same list, so `append` piles up across calls.

```python
def add(x, items=[]):   # one list, created at def time, shared forever
    items.append(x)
    return items
```

Fix: use `None` sentinel, make new list per call.

```python
def add(x, items=None):
    if items is None:
        items = []
    items.append(x)
    return items
```

Now `add(1)` gives `[1]`, `add(2)` gives `[2]`.