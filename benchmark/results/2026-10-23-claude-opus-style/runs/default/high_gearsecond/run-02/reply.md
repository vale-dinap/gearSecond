## Why immediate retries made it worse

**1. They multiply load exactly when the dependency can least handle it.** Every failed call turns into up to 6 calls (1 + 5 retries). A dependency that was struggling at 100% of normal traffic suddenly sees up to 6x. If it was failing because of overload, the retries keep it overloaded. It can't recover even after the original cause is gone. This is a *retry storm*, and it's a common way for a brief blip to turn into a long outage.

**2. "Immediately" means synchronized bursts.** With no delay, all retries land in the same instant. Every client that failed at time T retries at T+ε, and again at T+2ε. The dependency gets hit by waves of correlated traffic instead of a smooth stream, so it never gets a quiet moment to drain queues, warm caches, or let autoscaling catch up.

**3. Retries amplify across layers.** If service A retries 5× against B, and B retries 5× against C, then C sees up to 6 × 6 = 36x load from a single user request. Deep call chains with retries at every hop grow exponentially.

**4. They tie up the caller's own resources.** Threads, connections, and memory sit waiting on doomed calls. Latency rises, the caller's own clients time out (and often retry too), and the failure spreads upstream.

**5. Some failures aren't retryable at all.** Retrying a 400, 401, or 404, or a non-idempotent POST, wastes capacity. A non-idempotent POST can also cause duplicate side effects.

## A better retry policy

**Exponential backoff with jitter**
- Delay = `random(0, min(cap, base × 2^attempt))` ("full jitter"), e.g. base 100 ms, cap 10–20 s.
- Backoff gives the dependency breathing room. Jitter de-synchronizes clients so retries spread out instead of arriving in waves.

**Fewer attempts, bounded by a deadline**
- 2–3 retries at most, and all attempts must fit within the caller's overall timeout budget. Don't retry if the caller has already given up.
- Propagate deadlines downstream so inner services don't keep working on requests nobody is waiting for.

**Retry only what's safe and likely to help**
- Retry: connection errors, timeouts, 502/503/504, 429.
- Don't retry: 4xx client errors, or non-idempotent operations unless they use idempotency keys.
- Honor `Retry-After` headers on 429/503.

**Retry budget (the key protection against storms)**
- Cap retries as a fraction of traffic, e.g. retries ≤ 10% of requests over a sliding window (the token-bucket approach used by gRPC and Finagle).
- In normal times, occasional failures still get retried. During an outage, when most calls fail, the budget runs out and total load stays around 1.1x instead of 6x.

**Circuit breaker**
- When the error rate crosses a threshold, open the circuit and fail fast with no calls at all for a cooldown period.
- Then go half-open: let a few probe requests through, and close the circuit only if they succeed.
- This stops hammering a dead dependency and gives it room to recover. Pair it with a fallback (cached data, degraded response, queued work) where possible.

**Retry at one layer only**
- Pick one layer to own retries, typically the one closest to the user or the edge client. Other layers fail fast. This avoids multiplicative amplification.

### Example policy

```
max_attempts:      3 (1 initial + 2 retries)
backoff:           full jitter, base=100ms, cap=10s
overall deadline:  respect caller's timeout; no retry if <X ms remain
retry on:          connect errors, timeouts, 429, 502, 503, 504
respect:           Retry-After
retry budget:      retries <= 10% of requests (per client, sliding window)
circuit breaker:   open at >50% errors over 20+ requests in 10s;
                   30s cooldown; half-open with a few probes
idempotency:       retry non-idempotent calls only with idempotency keys
```

In short: immediate retries turn a failure into synchronized, multiplied load. The fix is to spread retries out in time (backoff + jitter), cap their total volume (budget + circuit breaker), and retry only where it can actually help.