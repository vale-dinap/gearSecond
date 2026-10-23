Default arg `[]` evaluated once, at `def` time. Same list object reused every call.

```python
add.__defaults__  # ([1, 2],) after two calls
```

- `add(1)`: appends to shared list -> `[1]`
- `add(2)`: appends to same list -> `[1, 2]`

Fix: default to `None`, make new list per call.

```python
def add(x, items=None):
    if items is None:
        items = []
    items.append(x)
    return items
```

Now `add(1)` -> `[1]`, `add(2)` -> `[2]`.