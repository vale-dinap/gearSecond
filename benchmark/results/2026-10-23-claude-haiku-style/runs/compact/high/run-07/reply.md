Mutable default arg. `items=[]` evaluated once at def time, same list object reused every call.

Trace:
- `add(1)`: `items` is the shared default list → append 1 → `[1]`
- `add(2)`: same list, now `[1]` → append 2 → `[1, 2]`

Fix: default to `None`, create fresh list per call.

```python
def add(x, items=None):
    if items is None:
        items = []
    items.append(x)
    return items
```

Now `add(1)` → `[1]`, `add(2)` → `[2]`.

Note: pass explicit list (`add(3, my_list)`) still mutates `my_list`. If you want no mutation, copy: `items = [] if items is None else list(items)`.