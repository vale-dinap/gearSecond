1. Create a B-tree index on `(customer_id, created_at DESC)` so the filter, sort, and `LIMIT 20` are satisfied by one index scan.
2. Select only the columns you need and add them with `INCLUDE` on that index so the query can be an index-only scan.
3. Run `EXPLAIN (ANALYZE, BUFFERS)` and `ANALYZE orders` to confirm the planner uses the index with accurate row estimates.