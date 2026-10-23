Default arg `[]` evaluated once, at `def` time. Same list object reused on every call that omits `items`.

```python
add(1)  # default list L is [] -> L.append(1) -> L = [1]
add(2)  # same L -> L.append(2) -> L = [1, 2]
```

Check: `add.__defaults__` holds that one list, and it keeps growing.

Fix: use `None` sentinel, create fresh list per call.

```python
def add(x, items=None):
    if items is None:
        items = []
    items.append(x)
    return items
```

Now `add(1)` -> `[1]`, `add(2)` -> `[2]`. Same rule for `{}`, `set()`, any mutable default.