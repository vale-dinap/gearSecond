Default arg evaluated once, at `def` time. Same list object reused every call that omits `items`. `append` mutates it, so state persists.

```python
>>> add.__defaults__
([1, 2],)
```

Fix: use `None` sentinel, build new list per call.

```python
def add(x, items=None):
    if items is None:
        items = []
    items.append(x)
    return items
```

Now `add(1)` → `[1]`, `add(2)` → `[2]`.