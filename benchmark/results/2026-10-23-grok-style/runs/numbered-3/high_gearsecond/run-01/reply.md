1. Create a composite B-tree index on `(customer_id, created_at DESC)` so the newest 20 rows for a customer are read directly from the index.
2. Select only the columns you need and `INCLUDE` them on that index so the query can be an index-only scan.
3. Run `ANALYZE orders` after the index exists so the planner’s statistics match a 50-million-row table.