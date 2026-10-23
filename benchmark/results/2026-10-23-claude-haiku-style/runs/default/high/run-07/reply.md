Immediate retries make an outage worse because they multiply load on a service that is already failing.

**Why it amplifies the outage**

- **Load multiplies.** Each request can produce up to 6 attempts (1 original + 5 retries). If the service normally sends 1,000 requests/s to its dependency, the outage can turn that into 6,000 requests/s. The dependency is already struggling, so the extra traffic keeps it down.
- **Retries land during the failure, not after it.** With no delay, every retry arrives while the dependency is still unhealthy, so most of them fail too. The retries add load and recover nothing.
- **Failures are correlated.** A dependency outage hits every caller at once, so all callers retry at the same moment. That creates synchronized bursts, a thundering herd, that hit the dependency each time it tries to come back.
- **Layers compound.** If the caller's caller also retries 5 times, the effect is multiplicative. Three layers each retrying 5 times means up to 6³ = 216 attempts per original request.
- **Recovery gets blocked.** A recovering service gets flattened by the retry surge the moment it comes back up, which can cause a cycle of recover, overload, fail.

**Retry policy I'd use instead**

1. **Exponential backoff with full jitter.** Wait `random(0, min(cap, base × 2^attempt))` between attempts, e.g. base 100 ms, cap 10 s. Growing delays give the dependency room to recover, and jitter spreads clients out so they don't retry in lockstep.
2. **Few attempts.** Cap total attempts at 2–3, not 6. Most transient errors clear quickly, and extra attempts mostly add load.
3. **Retry only what is safe and transient.** Retry timeouts, connection resets, 429, 502, 503, and 504. Don't retry 4xx errors other than 429, since they will fail again. Retry non-idempotent calls (like POSTs) only with an idempotency key.
4. **Honor `Retry-After`.** When the server says when to come back, wait at least that long.
5. **Retry budget.** Limit retries to a fraction of total traffic, e.g. retries may add no more than 10–20% extra load across the fleet. This caps amplification no matter how many clients there are.
6. **Circuit breaker.** After a threshold of consecutive failures, stop calling the dependency for a cooldown period and fail fast. Use periodic half-open probes to detect recovery.
7. **Timeouts and a deadline.** Set a per-attempt timeout and an overall deadline for the whole operation, so retries can't run indefinitely.
8. **Retry at one layer.** Decide which layer owns retries and keep the others to a single attempt. Otherwise the multiplication above applies.
9. **Observability.** Track retry counts, retry-budget exhaustion, and circuit state. Without these, retry storms are hard to see until the outage is already severe.

If you share the language or HTTP client library, I can show how to configure this policy there.