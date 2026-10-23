Immediate retries multiply load on a service that is already struggling.

**Why it made the outage worse**

- **Amplification:** With up to 5 retries, each failed call becomes up to 6 attempts. If the failure is a 1-in-N slowdown rather than a hard stop, that is roughly a 6x increase in requests to the dependency, arriving exactly when it has the least capacity.
- **No delay:** Retries fire before the dependency has any chance to recover, so each one adds to the queue rather than letting it drain.
- **Synchronization:** Many clients failing at the same moment retry at the same moment, producing traffic spikes that keep the dependency overloaded (a "retry storm").
- **Layered retries:** If callers upstream also retry, the multipliers compound. Three layers of 6 attempts is 216 requests per user action.
- **Wasted work on the caller:** Threads and connections stay tied up waiting, which can exhaust the caller's own resources and make its clients fail too.

**What I would use instead**

1. **Few attempts:** 2 to 3 total attempts, not 6.
2. **Exponential backoff with full jitter:** wait `random(0, min(cap, base * 2^attempt))`, for example base 200 ms, cap 10 s. Jitter spreads retries out so clients don't resynchronize.
3. **Retry only transient failures:** timeouts, connection resets, 429, 502, 503, 504. Don't retry other 4xx errors, since they will fail the same way again.
4. **Honor `Retry-After`:** if the dependency says when to come back, wait at least that long.
5. **Retry only idempotent operations,** or send an idempotency key so a retried POST can't create duplicates.
6. **A retry budget:** cap retries at a fraction of normal traffic (for example 10%). When the budget is exhausted, fail fast. This bounds the amplification no matter how many calls fail.
7. **A circuit breaker:** after a threshold of failures, stop calling the dependency for a cooldown period, then let a few probe requests through. This gives the dependency room to recover and frees the caller from waiting.
8. **Per-attempt timeouts plus an overall deadline,** so retries can't stretch one request indefinitely.
9. **Retry in one layer only.** Let the outermost or innermost caller own retries, not every hop.

With these in place, a dependency outage produces a bounded, smoothly decreasing load instead of a multiplying spike, and the breaker shows operators the failure directly.