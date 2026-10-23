## Why immediate retries make an outage worse

**1. They multiply load on a dependency that is already struggling.** If a call can make up to 5 retries, each failed request becomes 6 attempts. During a full outage, every incoming request produces 6 calls to the dependency instead of 1. The extra traffic arrives at the moment the dependency has the least capacity to absorb it, so it can't recover.

**2. The multiplication compounds across layers.** If the caller's caller uses the same policy, the effect is 6 × 6 = 36 attempts per user action. Three layers gives 216. Each layer's retries look reasonable on their own, but together they can produce a 100x traffic spike.

**3. Immediate retries synchronize.** Every instance of the service sees failures at roughly the same time and retries at roughly the same time, so the load arrives in waves rather than spread out. Each wave can push the dependency back down just as it starts to recover.

**4. They hold resources in the caller.** Each in-flight retry occupies a thread, connection, or socket. The caller's pool fills up with calls waiting on a dead dependency, and the caller starts failing requests for its own clients. That failure spreads upstream and triggers more retries there.

**5. Retrying transient-looking errors that aren't transient.** A dependency that is down for minutes will not succeed on attempts 2 through 6 separated by milliseconds. The retries only add cost.

## The retry policy I would use instead

**Retry only what is safe and likely to succeed:**
- Retry on connection errors, timeouts, 502, 503, 504, and 429 (honoring `Retry-After`).
- Do not retry other 4xx responses. They will fail the same way again.
- Retry non-idempotent operations (POST, payments) only with an idempotency key.

**Keep attempts low.** Two retries (3 total attempts) is usually enough to smooth over a blip. More rarely helps and mostly adds load.

**Back off exponentially with full jitter:**

```
sleep = random(0, min(cap, base × 2^attempt))
```

For example, with `base = 100ms` and `cap = 5s`, the waits are random values up to 100ms, then up to 200ms. Jitter spreads retries out so instances don't move in lockstep.

**Enforce a retry budget.** Limit retries to a fraction of total traffic, for example 10–20% of requests over a rolling window, using a token bucket. When the budget is spent, fail fast. This caps amplification no matter how many errors occur, which matters more than the per-call attempt count.

**Add a circuit breaker.** When the failure rate crosses a threshold (say 50% over 10 seconds), open the circuit and fail fast without calling the dependency. After a cooldown (say 30 seconds), let a few probe requests through (half-open). Close the circuit if they succeed. This gives the dependency room to recover.

**Respect a total deadline.** Propagate a request deadline so retries never run past what the caller is willing to wait. Don't start an attempt that can't finish before the deadline.

**Retry at one layer.** Decide where retries live and make other layers pass failures through. If every layer retries, the multiplication above happens.

**Degrade gracefully.** When the circuit is open, serve cached or partial data where possible, or return a clear error quickly instead of hanging.

**Monitor retry rate.** Track retries as a separate metric from requests. A rising retry ratio is an early warning of a dependency problem and of self-inflicted load.