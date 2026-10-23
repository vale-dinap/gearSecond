1. Create a composite B-tree index on `(customer_id, created_at DESC)` so Postgres can return the 20 newest rows for that customer without sorting.
2. Replace `SELECT *` with only the columns you need, and `INCLUDE` those columns on the index if you want an index-only scan.
3. Run `ANALYZE orders` and keep autovacuum current so the planner uses that index on a 50-million-row table.