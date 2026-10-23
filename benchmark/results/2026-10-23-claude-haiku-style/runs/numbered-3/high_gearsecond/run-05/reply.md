1. Add a composite index on `orders (customer_id, created_at DESC)` so Postgres can read the 20 rows in index order.
2. Run `EXPLAIN (ANALYZE, BUFFERS)` to confirm an Index Scan replaces the Seq Scan plus Sort, and check the actual row count.
3. Partition `orders` by range on `created_at` (or hash on `customer_id`) and keep `VACUUM`/`ANALYZE` current so the planner keeps choosing the index.