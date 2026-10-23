1. Add a composite B-tree index on `(customer_id, created_at DESC)` so the filter, sort, and `LIMIT 20` are satisfied by one index scan.
2. Replace `SELECT *` with only the columns you need and `INCLUDE` those columns on the index so the query can be index-only.
3. Run `ANALYZE orders` and confirm with `EXPLAIN (ANALYZE, BUFFERS)` that the planner uses that index and stops after 20 rows.