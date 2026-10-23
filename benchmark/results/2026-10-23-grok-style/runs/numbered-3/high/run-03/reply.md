1. Create a composite B-tree index on `(customer_id, created_at DESC)` so Postgres can seek that customer’s newest rows and stop at 20.
2. Select only the columns you need, and `INCLUDE` them on that index if you want an index-only scan.
3. Run `ANALYZE orders` and confirm with `EXPLAIN (ANALYZE, BUFFERS)` that the plan is an index scan that stops at `LIMIT 20`.