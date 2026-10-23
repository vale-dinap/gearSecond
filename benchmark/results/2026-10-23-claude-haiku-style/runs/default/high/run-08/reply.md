## Why immediate retries made the outage worse

**1. Retries multiply the load on a dependency that is already struggling.** With up to 5 retries, every failed call becomes up to 6 attempts. If the service normally sends 100 calls/s to the dependency, an outage can push that toward 600 calls/s. The dependency needs less load to recover, and it gets more.

**2. The multiplication compounds across layers.** If service A calls B and B calls C, and each retries 5 times, a single user request can reach C up to 6 × 6 = 36 times. Three layers give 216.

**3. Immediate retries don't give transient faults time to clear.** A failure caused by overload, a restart, or a brief network issue usually won't resolve in the next few milliseconds. The retries mostly land on the same failing condition.

**4. Failures are correlated, so retries synchronize.** Every client sees the outage at about the same time and retries on the same schedule. That creates repeated traffic spikes (a thundering herd) instead of spreading the load out.

**5. Retries hold caller resources.** Threads, connections, and memory stay occupied while attempts wait to fail. The service's own capacity runs out, so it starts failing for unrelated requests too.

## A better retry policy

**Limit attempts.** Start with 2 to 3 total attempts, not 6. Retries are for brief blips, and most outages outlast them.

**Use exponential backoff with full jitter.**
```
delay = random(0, min(cap, base * 2^attempt))
```
For example, base 200 ms and cap 10 s. Jitter spreads retries out so clients don't move in lockstep.

**Retry only transient errors.**
- Retry: timeouts, connection resets, 502, 503, 504, and 429 (honoring `Retry-After`).
- Don't retry: 400, 401, 403, 404, 422, and other client errors. Retrying them can't succeed.

**Retry only idempotent operations, or use idempotency keys.** Retrying a non-idempotent write, such as a payment, can duplicate its effect.

**Set a retry budget.** Allow retries only up to a fraction of total traffic, for example 10%. This caps amplification even when each request's policy looks reasonable on its own.

**Add a circuit breaker.** After a run of consecutive failures, stop calling the dependency for a cooldown period. Then let a few probe requests through (half-open). This fails fast during an outage and gives the dependency room to recover.

**Enforce an overall deadline.** Give each request a total time budget across all attempts, so retries can't outlast the caller's own timeout.

**Retry at one layer only.** Let the outermost or innermost client handle retries, not every hop. Otherwise the multiplication from point 2 applies.

**Monitor retry rates.** Alert when retries rise sharply. That is often the first visible sign of a dependency problem, and it shows whether your budget and breaker are working.

**Degrade gracefully.** When the circuit is open, return cached data, a reduced feature set, or a clear "temporarily unavailable" response instead of piling on more calls.