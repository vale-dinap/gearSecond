Default `items=[]` is created once, when Python defines `add`, and every call that skips `items` reuses that same list. First `add(1)` appends `1`. Second `add(2)` appends `2` onto the same list, so you get `[1, 2]`.

Fix: use `None` as the default and make a new list inside the function.

```python
def add(x, items=None):
    if items is None:
        items = []
    items.append(x)
    return items
```

Now each `add(1)` and `add(2)` gets its own list: `[1]`, then `[2]`. Pass your own list when you want to keep appending to it.