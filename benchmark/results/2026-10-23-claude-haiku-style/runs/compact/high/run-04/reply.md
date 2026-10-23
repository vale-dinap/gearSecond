Default arg `items=[]` evaluated once, at `def` time. Same list object reused every call. `append` mutates it, so state persists.

```python
add(1)  # items is the shared default list -> [1]
add(2)  # same list, now [1, 2]
```

Fix: use `None` sentinel, make new list per call.

```python
def add(x, items=None):
    if items is None:
        items = []
    items.append(x)
    return items
```

Now `add(1)` -> `[1]`, `add(2)` -> `[2]`.

Rule: never use mutable (`[]`, `{}`, `set()`) as default. Use `None`.