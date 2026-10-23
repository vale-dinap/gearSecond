1. Create a B-tree index on `(customer_id, created_at DESC)` so the filter, descending order, and `LIMIT 20` are served from the index without a sort.
2. Replace `SELECT *` with only the columns you need, and `INCLUDE` those columns on that index for an index-only scan.
3. Run `ANALYZE orders` and confirm with `EXPLAIN (ANALYZE, BUFFERS)` that the plan is an index scan that stops after 20 rows.