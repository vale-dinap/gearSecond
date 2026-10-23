Default `[]` built once, at `def` time, stored in `add.__defaults__`. Every call without `items` gets that same list object. `add(1)` appends 1 to it, `add(2)` appends 2 to the same list, so result is `[1, 2]`.

Fix: use `None` sentinel, make new list per call:

```python
def add(x, items=None):
    if items is None:
        items = []
    items.append(x)
    return items
```

Now `add(1)` → `[1]`, `add(2)` → `[2]`.

Same bug with `{}`, `set()`, or any mutable default. Immutable defaults (`0`, `""`, `()`, `None`) are safe.