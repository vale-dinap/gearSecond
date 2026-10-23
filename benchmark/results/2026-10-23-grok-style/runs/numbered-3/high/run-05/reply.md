1. Create a composite B-tree index on `(customer_id, created_at DESC)` so the filter, sort, and `LIMIT` are one index scan.
2. Replace `SELECT *` with only the columns you need, and `INCLUDE` them on that index for an index-only scan.
3. Run `ANALYZE orders` and `EXPLAIN (ANALYZE, BUFFERS)` to refresh statistics and confirm the planner uses the index.