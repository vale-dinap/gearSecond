1. Create a composite index on `(customer_id, created_at DESC)` so Postgres can fetch the newest 20 rows for that customer without sorting.
2. Replace `SELECT *` with only the columns you need and cover them in the index so the query can use an index-only scan.
3. Run `ANALYZE orders` so the planner has fresh statistics and chooses that index for selective `customer_id` values.