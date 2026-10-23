## Why immediate retries made the outage worse

- **Load amplification:** Each failed call becomes up to 6 calls (1 original + 5 retries). The dependency was already failing to keep up, so this adds the most load exactly when it has the least capacity.
- **Multiplication across layers:** If the caller chain has several services that each retry 5 times, the amplification compounds. Three layers with 6 attempts each can send up to 6³ = 216 requests for one user action.
- **No recovery time:** Immediate retries give the dependency no gap to drain queues, restart, or clear a backlog.
- **Correlated failures:** During an outage, retries mostly fail too, so they add load without adding successes.
- **Synchronized retry waves:** Without jitter, many clients that failed at the same moment retry at the same moment, creating spikes.
- **Held resources:** Each retry holds a connection, thread, or queue slot while it waits for a timeout, which can exhaust the caller's own resources.

## Retry policy I would use instead

1. **Few attempts:** Use at most 2 to 3 total attempts, not 6.
2. **Exponential backoff with full jitter:** Wait `random(0, min(cap, base × 2^attempt))`. For example, base 200 ms, cap 5 to 10 s. Jitter spreads retries out so clients don't move in lockstep.
3. **Retry only transient errors:** Retry on timeouts, connection resets, 502, 503, 504, and 429. Don't retry 4xx errors such as 400, 401, 403, or 404, since they will keep failing.
4. **Only idempotent operations, or ones with idempotency keys:** A retried POST that creates a payment or order can cause duplicates.
5. **Honor `Retry-After`:** If the dependency says when to come back, wait at least that long.
6. **Retry budget:** Cap retries to a fraction of total traffic, such as 10%. When the budget is spent, fail fast. This bounds amplification no matter how many attempts each call allows.
7. **Circuit breaker:** After a threshold of failures, stop calling the dependency for a cooldown period and return errors or fallbacks immediately. After the cooldown, let a few trial requests through (half-open) and close the circuit only if they succeed.
8. **Deadline propagation:** Give each user request an overall time budget, and stop retrying once that budget is spent.
9. **Retry at one layer only:** Choose one layer to own retries, usually the one closest to the failing call, and make other layers fail fast.

The core idea is that retries should be rare, spaced out, and bounded in total. Under an outage, the caller should shed load, not add to it.