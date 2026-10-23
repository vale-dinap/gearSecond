1. Create a composite B-tree index on `(customer_id, created_at DESC)` so Postgres can seek that customer’s rows already sorted and stop after 20.
2. Replace `SELECT *` with only the columns you need, and `INCLUDE` those columns on the index if you want an index-only scan.
3. Run `ANALYZE orders` and keep autovacuum current so the planner uses the index with accurate row estimates.