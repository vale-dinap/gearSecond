1. Create a B-tree index on `(customer_id, created_at DESC)` so the filter, order, and `LIMIT 20` are one index range scan.
2. Replace `SELECT *` with the columns you need and add them via `INCLUDE` so the plan can stay index-only.
3. Run `ANALYZE orders` after the index build and confirm with `EXPLAIN (ANALYZE, BUFFERS)` that it stops after 20 rows.