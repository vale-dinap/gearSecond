## Why immediate retries made the outage worse

**1. Retries multiply load on a dependency that is already struggling.** Each failed call becomes up to 6 requests (1 original + 5 retries). The dependency was already failing or overloaded, so the extra traffic pushes it further past capacity. Recovery becomes harder because the dependency gets no room to drain its queues and restart.

**2. Retries compound across layers.** If the caller's caller also retries 5 times, the multiplier is multiplicative. Three layers each doing 5 retries means up to 6³ = 216 attempts per user request reaching the bottom layer.

**3. Immediate retries arrive during the outage, not after it.** A retry sent a few milliseconds after a failure almost always lands while the cause is still present, so it fails too and adds to the pile.

**4. Synchronized retries create spikes.** When many clients fail at the same moment and retry with no delay or jitter, they all retry together. The dependency sees a wave of traffic each time, not a smooth load.

**5. The caller's own resources get exhausted.** Each slow or failing call holds a connection, thread, or memory while it waits and retries. The retrying service can run out of resources and fail for its own clients too.

## Retry policy I would use instead

- **Limit total attempts to 2–3**, not 6. Most transient failures resolve within one or two retries; more attempts mostly add load.
- **Use exponential backoff with full jitter:** `sleep = random(0, min(cap, base × 2^attempt))`, with base ≈ 100 ms and cap ≈ 10–30 s. Jitter spreads retries out so clients don't line up.
- **Retry only transient failures:** connection resets, timeouts, 429, 503, and 504. Don't retry 400, 401, 403, 404, or other errors that will fail the same way again.
- **Honor `Retry-After`** when the dependency sends it. The dependency is telling you when to come back.
- **Only retry idempotent operations**, or make them idempotent with idempotency keys. Otherwise a retry can duplicate a charge or a write.
- **Set a retry budget**, such as "retries may add at most 10% extra load," so retries can't grow with traffic during an outage.
- **Add a circuit breaker.** After a threshold of failures, stop calling the dependency for a cooling-off period and fail fast. Let a few trial requests through (half-open) to detect recovery.
- **Enforce an end-to-end deadline** for each user request, so retries stop once the caller has no time left to use the result.
- **Retry at one layer only.** Let the service closest to the failing dependency retry and have the layers above it fail fast, or the multiplication from point 2 returns.
- **Monitor retry rates and circuit state** so you can see amplification before it becomes an outage.

The core idea is that retries should be rare, spaced out, bounded in number, and stopped entirely when the dependency is clearly down. Immediate, unbounded-in-aggregate retries turn a partial failure into a full one.