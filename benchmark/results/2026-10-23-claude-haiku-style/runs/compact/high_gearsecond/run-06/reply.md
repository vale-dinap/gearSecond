Default `[]` is evaluated once, when `def` runs. Every call that omits `items` gets that same list object, so `append` mutates it.

- `add(1)`: appends 1 to shared list -> `[1]`
- `add(2)`: appends 2 to same list -> `[1, 2]`

Fix: use `None` as sentinel, make new list per call.

```python
def add(x, items=None):
    if items is None:
        items = []
    items.append(x)
    return items
```

Now `add(1)` -> `[1]`, `add(2)` -> `[2]`.