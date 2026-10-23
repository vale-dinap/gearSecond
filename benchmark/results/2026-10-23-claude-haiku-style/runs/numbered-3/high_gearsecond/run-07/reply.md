1. Add a composite index on `orders (customer_id, created_at DESC)` so Postgres can read the 20 newest rows per customer directly.
2. Use `CREATE INDEX CONCURRENTLY` for that index to avoid blocking writes on the 50M-row table during the build.
3. Run `ANALYZE orders` and check `EXPLAIN (ANALYZE, BUFFERS)` to confirm an Index Scan replaces the sort and the planner uses it.