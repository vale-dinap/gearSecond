1. Add composite index `CREATE INDEX CONCURRENTLY ON orders (customer_id, created_at DESC);` so the filter and sort come from one index scan.
2. Run `EXPLAIN (ANALYZE, BUFFERS)` on the query to confirm the plan uses an index scan and not a sort over a large set.
3. Keep `orders` partitioned by `created_at` (or archive old rows) so each query touches less data.