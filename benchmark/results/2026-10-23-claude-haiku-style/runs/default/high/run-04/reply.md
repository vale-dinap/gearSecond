## Why immediate retries made the outage worse

**1. Retries multiply load on a service that is already failing.** A call that fails gets up to 6 attempts (1 original + 5 retries). If every call fails during the outage, the dependency receives about 6x its normal traffic at the moment it has the least capacity. Retries are supposed to help with transient faults, but during a real outage nearly every attempt fails, so the retries are almost all extra load.

**2. Retries compound across layers.** If the caller's own callers also retry, the multiplier stacks. Three services each doing 6 attempts yield 6³ = 216 requests to the bottom dependency for one user action.

**3. No delay means no recovery time.** Immediate retries arrive within milliseconds, so they land while the dependency is still overloaded. Its queues grow, its timeouts fire, and more requests fail, which triggers more retries. This is a feedback loop.

**4. Clients retry in sync.** Many instances that failed at the same moment retry at the same moment, producing synchronized waves (a thundering herd) instead of a smoothed load.

**5. Resources are held longer.** Each retry consumes threads, connections, and sockets in the calling service. Its own pools fill up and it starts failing too, spreading the outage upstream.

**6. Blind retries can repeat side effects.** If the failed call was a non-idempotent write that actually succeeded before the error was returned, retrying can create duplicates.

## Retry policy I would use instead

- **Retry only retryable failures.** Retry on connection errors, timeouts, 502/503/504, and 429 (honoring `Retry-After`). Do not retry other 4xx responses, since they will fail the same way again.
- **Use exponential backoff with full jitter.** Wait `random(0, min(cap, base × 2^attempt))`. The growing delay gives the dependency room to recover, and the randomness spreads clients out. A reasonable starting point is a base of 100 ms and a cap of 10–30 s.
- **Keep the attempt count low.** Two or three total attempts is usually enough for transient faults. More attempts mostly add load during a sustained outage.
- **Add a retry budget.** Allow retries only up to a fraction of normal traffic (for example, retries may add no more than 10–20% extra requests). Once the budget is spent, fail fast. This caps amplification regardless of how many clients are failing.
- **Use a circuit breaker.** After a threshold of failures, stop calling the dependency for a cooldown period, then let a few probe requests through. This prevents hammering a dependency that is down and gives it time to recover.
- **Retry at one layer only.** Retry at the edge or at the immediate client, not at every hop. Otherwise the multipliers stack.
- **Set an overall deadline.** Propagate a deadline so retries stop once the caller's time budget is gone, rather than continuing after the user has given up.
- **Make writes idempotent before retrying them.** Send an idempotency key so the server can deduplicate a repeated write.
- **Monitor retry rates.** Alert on the ratio of retries to first attempts. A sudden rise is an early warning of a dependency problem and of a retry storm.

In short: retry a little, retry slowly with jitter, cap the total retry volume, stop calling a service that is clearly down, and retry at only one layer.