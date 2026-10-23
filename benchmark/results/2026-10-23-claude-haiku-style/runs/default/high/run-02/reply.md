## Why immediate retries made the outage worse

- **Retries multiply load on a service that is already failing.** Each failed call becomes up to 6 calls (1 original + 5 retries). The dependency was struggling, and the caller sent up to six times as much traffic at the moment it had the least capacity.
- **Multiple layers compound the effect.** If three services in a chain each retry 5 times, one user request can produce 6³ = 216 calls to the bottom dependency.
- **Immediate retries arrive too fast to help.** With no delay, retries usually hit the same overloaded instance or the same unhealthy state within milliseconds, so they almost always fail too.
- **Retries synchronize.** Many clients fail at the same moment and retry on the same schedule, creating traffic spikes that hit the dependency in waves.
- **The outage sustains itself.** Load does not drop when the dependency is down, so it cannot recover. This is a metastable failure: the retry logic keeps the system in the broken state even after the original trigger is gone.
- **Caller resources stay tied up.** Threads, connections, and queue slots held by pending retries can exhaust the caller, which then fails for unrelated requests too.

## Retry policy I would use instead

1. **Few attempts.** Use 1 original attempt plus at most 2 retries, not 5.
2. **Exponential backoff with full jitter.** Wait `random(0, min(cap, base × 2^attempt))`, for example with base 100 ms and cap 5–10 s. Backoff gives the dependency room to recover, and jitter spreads retries out so clients do not retry in lockstep.
3. **Retry only transient failures.** Retry connection resets, timeouts, 502, 503, 504, and 429. Do not retry most other 4xx responses, since they will fail again. For 429 and 503, honor the `Retry-After` header.
4. **Use a retry budget.** Cap retries at a fraction of total traffic, such as 10% over a rolling window. When the budget is exhausted, fail fast instead of retrying. This bounds amplification regardless of how many clients are affected.
5. **Add a circuit breaker.** After a threshold of consecutive failures, stop calling the dependency for a cooldown period and return an error or fallback immediately. Use half-open probes to detect recovery.
6. **Set an overall deadline.** Give each request a total time budget that covers all attempts, so retries cannot run long past the caller's timeout.
7. **Make retried operations idempotent.** For non-idempotent calls such as POSTs, use idempotency keys so a retry after an ambiguous failure does not create duplicate side effects.
8. **Retry at one layer only.** Let the outermost or innermost layer own retries, not every hop, to avoid the multiplicative effect.
9. **Monitor retry rates.** Track retries per request and the budget and breaker states, and alert when they spike. A rising retry rate is an early sign of a dependency problem.