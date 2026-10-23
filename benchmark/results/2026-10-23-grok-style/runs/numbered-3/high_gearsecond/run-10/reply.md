1. Add a composite B-tree index on `(customer_id, created_at DESC)` so the planner can seek that customer and stop after 20 rows.
2. Replace `SELECT *` with only the columns you need, and include those columns in the index so the query can be index-only.
3. Run `ANALYZE orders` and raise the statistics target on `customer_id` so the planner estimates the 20-row limit correctly.