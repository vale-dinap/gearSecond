1. Add a composite index on `orders (customer_id, created_at DESC)` so Postgres can read the 20 newest rows directly.
2. Run `EXPLAIN (ANALYZE, BUFFERS)` to confirm an Index Scan replaces the Seq Scan plus Sort.
3. Consider partitioning `orders` by `created_at` range if the table keeps growing and old data is rarely queried.