## Why immediate retries made the outage worse

- **Load multiplies.** Each failed call becomes up to 6 calls (1 original + 5 retries). If the dependency is already overloaded, its incoming traffic can grow by up to 6x just as it is trying to recover.
- **Retries arrive at the worst moment.** A dependency that is failing is usually slow or saturated. Immediate retries add work to the queue that is already backed up, so more requests time out, which triggers more retries.
- **Clients synchronize.** Many instances fail at the same moment and retry at the same moment, so the dependency sees repeated synchronized spikes instead of a smooth load it could absorb.
- **No time to recover.** A dependency often needs seconds or minutes to restart, clear a queue, or refill connection pools. Retrying instantly gives it none of that time.
- **Amplification compounds across layers.** If A calls B and B calls C, and each retries 5 times, C can receive 36x the normal traffic (6 × 6).

## A better retry policy

1. **Retry only transient failures.** Retry on connection resets, timeouts, `429`, `502`, `503`, and `504`. Don't retry on `4xx` errors like `400` or `404`, since they will fail again.
2. **Use exponential backoff with full jitter.** Wait `random(0, min(cap, base × 2^attempt))`, for example with base 100 ms and cap 10 s. Growing delays give the dependency room to recover, and jitter spreads clients out.
3. **Keep the attempt count small.** Two or three total attempts is usually enough. More attempts rarely succeed when the outage lasts longer than the retry window.
4. **Honor `Retry-After`.** If the dependency says when to come back, wait at least that long.
5. **Add a retry budget.** Allow retries only while they stay under a fraction of normal traffic (for example, 10%). This caps amplification no matter how many clients are failing.
6. **Use a circuit breaker.** After a threshold of failures, stop calling the dependency for a cooldown period and fail fast. Send occasional trial requests (half-open state) to check for recovery.
7. **Set an overall deadline.** Pass a timeout budget through the call chain so retries cannot run past what the caller will wait for.
8. **Make retries safe.** Retry non-idempotent operations (such as `POST`) only with an idempotency key, so a retry after a timeout doesn't create duplicates.
9. **Retry at one layer only.** Let either the client library or the service retry, not both, to avoid multiplicative amplification.

A sketch of the core logic:

```python
def call_with_retry(fn, max_attempts=3, base=0.1, cap=10.0):
    for attempt in range(max_attempts):
        try:
            return fn()
        except TransientError as e:
            if attempt == max_attempts - 1:
                raise
            delay = random.uniform(0, min(cap, base * 2 ** attempt))
            if e.retry_after is not None:
                delay = max(delay, e.retry_after)
            time.sleep(delay)
```

This should be combined with the retry budget and circuit breaker, since backoff alone does not prevent a fleet of clients from collectively overwhelming a recovering dependency.