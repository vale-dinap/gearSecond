1. Add a composite index on `orders (customer_id, created_at DESC)` so Postgres can walk the matching rows in order and stop after 20.
2. Use `SELECT` with only the columns you need instead of `*`, so the index can serve the query more often and less data is read.
3. Run `EXPLAIN (ANALYZE, BUFFERS)` on the query to confirm it uses an Index Scan and not a Sort over a large set of rows.