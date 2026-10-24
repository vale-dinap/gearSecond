**Why it worsened the outage:**
- Immediate retries flood a failing dependency with identical requests
- Amplifies load on already exhausted CPU, memory, DB connections, or bandwidth
- Prevents the dependency from recovering (thundering herd / retry storm)
- Cascades timeouts and resource exhaustion to other services waiting on the same dependency

**Better retry policy:**
- **Exponential backoff:** 1s → 2s → 4s → 8s → 16s (or similar)
- **Jitter:** randomize each interval ±20–30% to desynchronize clients
- **Respect `Retry-After` headers** when the dependency provides them
- **Circuit breaker:** pause all retries after N consecutive failures or a time window, then probe lightly
- **Filter non-retryable errors:** skip 4xx (except 429/503), cacheable responses, or idempotent-safe checks
- **Enforce max retry limit + per-request timeout:** stop after 3–5 attempts or total elapsed time exceeds SLA threshold

This shifts retries from a synchronous load multiplier to a controlled, self-regulating recovery mechanism.