## Why immediate retries made the outage worse

- **Load multiplies during the outage.** Each failed call becomes up to 6 calls (1 original + 5 retries). The dependency is already failing to keep up, so the extra load pushes it further behind.
- **Retries land before recovery.** With no delay, the retries arrive in the same second as the failure, when the dependency is least able to respond.
- **Clients retry in sync.** Many callers fail at the same moment and retry at the same moment, so the dependency gets bursts instead of a smooth flow.
- **Amplification compounds across layers.** If the caller's own callers also retry, the multiplier stacks: 6 × 6 = 36 calls for one user request, and so on.
- **The caller's resources drain.** Threads, connections and queue slots stay occupied by retrying calls, so the caller also slows down or fails.
- **Slow calls get duplicated.** If a request timed out but actually succeeded, the retry repeats work, which matters for non-idempotent operations.

## Retry policy I would use instead

1. **Retry only transient failures.** Retry on connection resets, timeouts, 502, 503, 504, and 429. Do not retry other 4xx errors, since they will fail again. Retry 5xx only when the operation is idempotent or has an idempotency key.
2. **Cap attempts low.** Use at most 2 or 3 total attempts, not 6.
3. **Exponential backoff with full jitter.** Wait a random time between 0 and `min(cap, base × 2^attempt)`. For example, base 200 ms and cap 10 s. The jitter spreads retries out so they don't arrive together.
4. **Honor `Retry-After`.** If the dependency says when to come back, wait at least that long.
5. **Use a retry budget.** Allow retries only up to a fixed fraction of normal traffic, for example 10%. When the budget is spent, fail fast. This bounds amplification no matter how many calls fail.
6. **Add a circuit breaker.** After a failure rate threshold, stop calling the dependency for a cooldown period, then let a few probe requests through (half-open). This stops the flood entirely while the dependency recovers.
7. **Set an overall deadline.** Give each request a total time budget that includes retries, so retries can't keep a call alive indefinitely.
8. **Retry at one layer only.** Pick the layer closest to the dependency, or the edge, and make other layers pass failures through.
9. **Make writes idempotent.** Send an idempotency key with non-idempotent POSTs so a duplicate retry is safe.
10. **Monitor it.** Track retry rate, breaker state and budget exhaustion, and alert when the retry rate spikes.

Pseudocode for the core loop:

```
for attempt in 1..3:
    if breaker.open() or budget.exhausted() or deadline passed: fail fast
    result = call(dependency, timeout=remaining_deadline)
    if success or not transient(result): return result
    sleep(random(0, min(10s, 200ms * 2^attempt)))  // or Retry-After if larger
fail
```