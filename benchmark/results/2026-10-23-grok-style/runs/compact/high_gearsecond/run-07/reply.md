Default `items=[]` is created once, when Python defines `add`, and reused on every call that omits `items`. First `add(1)` appends into that same list. Second `add(2)` appends into it again, so you get `[1, 2]`.

Fix: use `None` as the default and make a new list inside the function.

```python
def add(x, items=None):
    if items is None:
        items = []
    items.append(x)
    return items
```

Now each call with no `items` gets its own list. `add(1)` returns `[1]`. `add(2)` returns `[2]`. Passing a list still mutates that list: `add(3, [1, 2])` returns `[1, 2, 3]`.