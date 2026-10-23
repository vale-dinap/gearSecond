Immediate retries multiply load on a dependency that is already failing. If the service sends each failed call up to 5 times with no delay, one request becomes up to 6 attempts. Every caller does this at once, so the dependency can see 5 to 6 times its normal traffic exactly when it has the least capacity to absorb it. Retries that arrive in the same instant also synchronize into bursts, so each recovery window is hit again before the dependency can stabilize. And if the dependency is failing because it's overloaded, the extra traffic keeps it overloaded. The retries become the cause of the outage's duration, not just a response to it.

I would use this policy instead:

- **Retry only transient errors.** Retry timeouts, connection resets, 429, 503, and 504. Don't retry 400, 401, 403, 404, or other errors where the same request will fail the same way.
- **Cap the attempts low.** Two or three total attempts is usually enough. Five is rarely justified.
- **Use exponential backoff with jitter.** Start around 100 to 500 ms, double each attempt, cap at a few seconds, and randomize each delay (full jitter, e.g., `sleep = random(0, min(cap, base * 2^attempt))`). Jitter spreads retries out so callers don't line up.
- **Respect `Retry-After`.** If the dependency sends a 429 or 503 with this header, wait at least that long.
- **Budget retries across the fleet.** Limit retries to a fraction of total traffic, for example 10%, so retries can't exceed a set share of normal load. Retry budgets or token buckets work for this.
- **Use a circuit breaker.** After a threshold of consecutive failures, stop calling the dependency for a cooldown period. Let a few probe requests through to test recovery (half-open state). This prevents the service from hammering a dependency that is clearly down.
- **Set an overall deadline.** Retries should stop when the caller's total time budget is spent, so retries don't pile up behind slow requests.
- **Make retried operations idempotent.** Use idempotency keys for non-GET calls so a retry after an ambiguous failure doesn't duplicate side effects.

The most important changes are the backoff with jitter and the circuit breaker. Together they reduce load during an outage and let the dependency recover.