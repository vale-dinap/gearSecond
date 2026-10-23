1. Add composite index: `CREATE INDEX CONCURRENTLY ON orders (customer_id, created_at DESC);`
2. Run `EXPLAIN (ANALYZE, BUFFERS)` to confirm an Index Scan replaces the Seq Scan plus Sort.
3. Use keyset pagination (`WHERE created_at < $last_seen`) instead of large OFFSETs for deeper pages.