The default `items=[]` is built once, when Python defines `add`. Every call that skips `items` gets that same list object. `add(1)` appends `1`. `add(2)` appends `2` onto the list that already holds `1`, so the result is `[1, 2]`.

Make a new list inside the function when the caller does not pass one:

```python
def add(x, items=None):
    if items is None:
        items = []
    items.append(x)
    return items
```

`None` is created once too, but it is immutable and only a sentinel. The `[]` runs on each call that needs a fresh list.