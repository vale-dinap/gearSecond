Default `[]` is built once, when `def` runs, not per call. Every call that omits `items` gets that same list object. `append` mutates it, so state leaks between calls:

```python
add(1)  # default list becomes [1], returned
add(2)  # same list, now [1, 2], returned
```

Check: `add.__defaults__` shows the shared list growing.

Fix: use `None` sentinel, create fresh list per call:

```python
def add(x, items=None):
    if items is None:
        items = []
    items.append(x)
    return items
```

Now `add(1)` → `[1]`, `add(2)` → `[2]`.

Rule: never use mutable literal (`[]`, `{}`, `set()`) as default. Use `None`, create inside body.