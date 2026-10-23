Immediate retries multiply the load on a dependency exactly when it has the least capacity to absorb it.

**Why it made the outage worse**

- **Load amplification.** With 1 original attempt and 5 retries, each failing request becomes up to 6 requests. If the dependency is already overloaded, the retries add load on top of the traffic that was already too much for it. Recovery stalls because the dependency never gets a window to drain its queues.
- **Multiplication across layers.** If the service sits behind another retrying caller, the factors compound. Two layers with 6 attempts each can send up to 36 requests for every original one.
- **Synchronized retries.** Many clients failing at the same moment all retry at the same moment, since they have no delay or jitter. That produces a spike at each retry interval rather than a smooth load, which is a thundering herd.
- **Resource holding.** Each failed attempt can hold connections, threads, or memory for the full timeout. Retrying immediately keeps the caller's own pools full, so the caller degrades too.
- **Retrying errors that won't clear.** A 400 or 404 will fail again, and a 429 or 503 needs time to pass. Immediate retries waste capacity on requests that cannot succeed.
- **Recovery storm.** When the dependency comes back, every queued retry hits it at once, so it can fall over again immediately.

**A better policy**

1. **Exponential backoff with full jitter.** Wait `random(0, min(cap, base × 2^attempt))`. For example, use a base of 200 ms and a cap of 10 s. The randomness spreads clients out so they don't retry in lockstep.
2. **Few attempts.** Use 2 or 3 total attempts, not 6. Retries are for transient faults, and a longer tail adds little.
3. **A retry budget.** Limit retries to a fraction of total traffic, such as 10%, using a token bucket or a ratio check. This caps amplification regardless of how many requests fail. Retries are only allowed while the budget has tokens.
4. **Retry only what's safe and useful.** Retry timeouts, connection resets, 502, 503, 504, and 429. Don't retry other 4xx codes. Retry non-idempotent operations only with an idempotency key.
5. **Honor `Retry-After`.** If the dependency says when to come back, wait at least that long.
6. **Use a circuit breaker.** After a threshold of failures, stop calling the dependency for a cooldown period and fail fast. Then let a few trial requests through (half-open) before resuming. This is what actually stops the storm during an outage.
7. **Respect an overall deadline.** Set a total time budget for the request and per-attempt timeouts within it. Don't retry once the budget is spent.
8. **Retry at one layer.** Let one layer own retries and have the others fail fast, so the multiplication never happens.

In short, the original policy retried too many times, too soon, in sync, and without limit. The replacement waits progressively longer with randomness, caps total attempts and the share of traffic retries can add, stops calling a dependency that is clearly down, and retries only errors that might succeed on a later try.