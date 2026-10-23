1. Create a composite B-tree index on `(customer_id, created_at DESC)` so Postgres can seek that customer and return the newest 20 rows without sorting.
2. Replace `SELECT *` with the columns you need and `INCLUDE` them on that index so the query is index-only.
3. Run `EXPLAIN (ANALYZE, BUFFERS)` and `ANALYZE orders` to confirm an index scan and refresh the planner’s row estimates.