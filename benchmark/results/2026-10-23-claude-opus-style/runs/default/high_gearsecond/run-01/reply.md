## Why immediate retries made it worse

**1. They multiply load exactly when the dependency can least handle it.**
With up to 5 retries, every failing request becomes up to 6 requests. If the dependency is struggling at 1,000 req/s, your service can turn that into 6,000 req/s. A dependency that was degraded becomes saturated, and one that was trying to recover gets pushed back down. This is a *retry storm*.

**2. Immediate retries are synchronized.**
Every client sees the failure at roughly the same moment and retries at roughly the same moment. That produces waves of traffic aligned in time (a *thundering herd*), instead of load spread out evenly. A recovering server gets hit by a spike right as it comes back up.

**3. Retrying immediately almost never helps.**
Outages, overloads, GC pauses, failovers, and restarts last seconds to minutes. A retry 2 ms later hits the same broken state, so you pay the full cost of the retry and get nothing back.

**4. It amplifies through layers.**
If A calls B calls C, and each layer retries 5 times, a failure at C produces up to 6 × 6 = 36 calls from one user request. Deep call chains turn modest retry counts into huge amplification.

**5. It ties up your own resources.**
Threads, connections, and sockets sit busy cycling through retries. Your service's latency climbs, its pools fill up, and its own callers start timing out and retrying. The outage spreads upstream.

**6. Some failures shouldn't be retried at all.**
Blindly retrying 400s, 401s, or non-idempotent POSTs wastes capacity and can cause duplicate side effects.

## The retry policy I'd use instead

**Only retry what's retryable**
- Retry: connection errors, timeouts, 502/503/504, and 429.
- Don't retry: other 4xx, or non-idempotent operations unless they carry an idempotency key.
- Honor `Retry-After` on 429/503.

**Exponential backoff with jitter**
- Delay ≈ `random(0, min(cap, base * 2^attempt))` ("full jitter").
- Example: base 100 ms, cap 10–30 s.
- Backoff gives the dependency time to recover. Jitter de-synchronizes clients so retries don't arrive in waves.

**Fewer attempts, bounded by a deadline**
- 2–3 retries, not 5.
- Bound the whole operation by a total time budget or deadline, and propagate that deadline downstream so nobody keeps retrying work whose caller already gave up.

**A retry budget**
- Cap retries at a fraction of normal traffic, e.g. retries may be at most 10% of requests over a sliding window (a token bucket works well).
- In normal times a few retries smooth over blips. During a real outage the budget runs out quickly and load stays close to 1×, not 6×.

**A circuit breaker**
- When the error rate crosses a threshold, open the circuit and fail fast, with no calls to the dependency.
- After a cooldown, go half-open and let a few probe requests through. Close the circuit once they succeed.
- This stops hammering the dependency and frees your own threads.

**Retry at one layer only**
- Pick one layer (usually the outermost or the one closest to the failing call) to own retries. The others fail fast. This avoids multiplicative amplification.

**Degrade gracefully when retries are exhausted**
- Serve cached or stale data, a default response, or a fast clear error. Don't hang.

### Summary

| Before | After |
|---|---|
| Retry everything | Retry only transient, idempotent failures |
| 0 ms delay | Exponential backoff + full jitter, honor `Retry-After` |
| 5 retries | 2–3 retries within a total deadline |
| Unlimited retry volume | Retry budget (~10% of traffic) |
| Keep calling a dead dependency | Circuit breaker, fail fast |
| Every layer retries | One layer retries |

The core idea: retries should help with *brief, random* failures and get out of the way during *sustained* ones. Immediate unbounded retries do the opposite. They add the most load exactly when the system is least able to handle it.