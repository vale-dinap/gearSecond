## Why immediate retries made the outage worse

- **Load multiplies.** Each failed call becomes up to 6 calls (1 original + 5 retries). If the dependency is already overloaded, the service adds 5x its normal traffic exactly when the dependency has the least capacity.
- **Retries are synchronized.** Calls that fail together retry together, so the dependency gets bursts instead of a smooth load. Each burst can knock it over again just as it begins to recover.
- **Retries don't spread out over time.** With no delay, the retries land within milliseconds, before the dependency has any chance to recover from the first failure.
- **Amplification compounds across layers.** If the caller's own callers also retry, the multiplier grows geometrically. Three layers each retrying 5 times means up to 216 attempts for one user request.
- **Failing calls hold resources.** Threads, connections, and queue slots stay occupied during retries, so the calling service slows down and can fail on its own.

## Retry policy I would use instead

1. **Exponential backoff with full jitter.** Wait `random(0, min(cap, base * 2^attempt))`. For example, base 100 ms and cap 10 s. The jitter spreads retries out so clients don't stampede together.
2. **Few attempts, bounded total time.** Two or three attempts at most, plus an overall deadline per request. Stop retrying when the deadline passes, even if attempts remain.
3. **Retry only transient failures.** Retry on timeouts, connection resets, 502/503/504, and 429. Don't retry 400, 401, 403, 404, or other errors that will fail the same way again.
4. **Honor `Retry-After`.** If the dependency says when to come back, wait at least that long.
5. **A retry budget.** Limit retries to a fraction of normal traffic, such as 10%. When the budget is exhausted, fail fast. This caps amplification no matter how many requests fail.
6. **A circuit breaker.** After a threshold of failures, stop calling the dependency for a cooldown period. Let a few trial requests through (half-open) before resuming normal traffic. This gives the dependency room to recover.
7. **Retry at one layer only.** Pick one place to own retries, usually the outermost caller or the client library, so the multipliers don't stack.
8. **Make retried operations idempotent.** Use idempotency keys for non-idempotent calls such as payments or creates, so a retry after a timeout doesn't duplicate the effect.

In short: back off with jitter, cap attempts and total time, retry only transient errors, limit retries to a budget, and use a circuit breaker so a failing dependency gets less traffic, not more.