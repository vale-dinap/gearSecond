Default `[]` is built once, when `def` runs, not per call. Every call that omits `items` reuses that same list object.

- `add(1)`: appends `1` to the shared list, returns it -> `[1]`
- `add(2)`: same list, appends `2` -> `[1, 2]`

`.append` mutates in place, so the shared list keeps growing. Also, the list returned by `add(1)` is that same object, so it changes too.

Fix: use `None` as sentinel, make new list per call:

```python
def add(x, items=None):
    if items is None:
        items = []
    items.append(x)
    return items
```

Now `add(1)` -> `[1]`, `add(2)` -> `[2]`.