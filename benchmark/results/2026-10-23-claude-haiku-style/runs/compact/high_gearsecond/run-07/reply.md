Default list made once at `def` time, shared across calls. `append` mutates that same object, so `add(1)` leaves `[1]` in it, and `add(2)` appends to it → `[1, 2]`.

Fix: use `None` sentinel, build new list per call:

```python
def add(x, items=None):
    if items is None:
        items = []
    items.append(x)
    return items
```

Now `add(1)` → `[1]`, `add(2)` → `[2]`.