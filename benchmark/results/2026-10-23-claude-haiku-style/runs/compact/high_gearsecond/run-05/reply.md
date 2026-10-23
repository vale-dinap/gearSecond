Default `[]` is evaluated once, at `def` time. Every call that uses the default gets that same list object, so `append` mutates it for all later calls.

```python
>>> add(1)
[1]
>>> add(2)   # same list, already holds 1
[1, 2]
```

Fix: default to `None`, create a fresh list per call.

```python
def add(x, items=None):
    if items is None:
        items = []
    items.append(x)
    return items
```

Now `add(1)` -> `[1]`, `add(2)` -> `[2]`.

Mutable defaults (`list`, `dict`, `set`) have this trap. Immutable defaults (`int`, `str`, `tuple`, `None`) don't.