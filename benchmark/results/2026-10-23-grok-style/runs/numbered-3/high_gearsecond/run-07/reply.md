1. Add a composite index on `(customer_id, created_at DESC)` so Postgres can seek that customer's newest rows and stop at 20.
2. Select only the columns you need and `INCLUDE` them on that index so the plan can stay index-only.
3. Run `ANALYZE orders` and `EXPLAIN (ANALYZE, BUFFERS)` to confirm the index is used and the statistics match 50 million rows.