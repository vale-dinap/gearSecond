1. Add a composite index: `CREATE INDEX CONCURRENTLY ON orders (customer_id, created_at DESC);`
2. Confirm with `EXPLAIN (ANALYZE, BUFFERS)` that the plan is an index scan with no sort node.
3. Run `VACUUM ANALYZE orders;` (and check autovacuum) so the planner has current statistics and a visibility map.