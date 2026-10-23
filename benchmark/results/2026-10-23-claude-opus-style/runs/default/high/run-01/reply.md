## Why immediate retries made the outage worse

**1. Load amplification.** Each failing request becomes up to 6 attempts (1 + 5 retries). When the dependency is already overloaded, your service multiplies its traffic by as much as 6× exactly when it can least handle it. If several layers each retry (A→B→C, each retrying 5×), it compounds: 6 × 6 = 36× at the bottom.

**2. No recovery window.** Immediate retries leave no gap for the dependency to shed load, drain queues, restart, or fail over. A dependency that might have recovered under normal load stays pinned at saturation. That turns a transient blip into a sustained outage, sometimes called a *retry storm* or *metastable failure*. The system stays broken even after the original trigger is gone, because retry traffic alone keeps it overloaded.

**3. Synchronized bursts.** All clients that failed at the same moment retry at the same moment, so the load arrives in coordinated waves instead of spreading out.

**4. Resource exhaustion on your side.** Threads, connections, and sockets are tied up in retry loops. Latency climbs, upstream callers time out and retry *your* service, and the failure spreads outward.

**5. Retrying the wrong things.** Blind retries often include errors that will never succeed on retry (400s, auth failures) or that the server explicitly flagged as overload (429, 503 with `Retry-After`).

## A better retry policy

**Exponential backoff with jitter.** Wait `random(0, min(cap, base × 2^attempt))` before each retry ("full jitter"). For example, use base 100 ms and cap 10–30 s. The backoff gives the dependency time to recover, and the randomness desynchronizes clients.

**Fewer attempts.** Two or three retries is usually plenty. Beyond that you mostly add load and latency.

**Retry only retryable failures.**
- Retry: connection errors, timeouts, 502/503/504, and 429 (honoring `Retry-After`).
- Don't retry: other 4xx errors.
- Only retry non-idempotent requests (e.g. POST) if they carry an idempotency key.

**Retry budget.** Cap retries as a fraction of total traffic, for example retries may not exceed 10% of requests over a sliding window. In a healthy system this costs nothing. During an outage it automatically limits amplification to about 1.1× instead of 6×.

**Circuit breaker.** After the failure rate crosses a threshold, stop calling the dependency for a cooldown period and fail fast or serve a fallback (cached or degraded response). Then let a few probe requests through (half-open state) and close the circuit once they succeed. This gives the dependency real breathing room.

**Retry at one layer only.** Pick one layer, usually the one closest to the user or the one with the most context, and have the others fail fast. This avoids multiplicative amplification across the stack.

**Deadline awareness.** Propagate the overall request deadline and don't start a retry that can't finish in time. Retrying after the caller has already given up is pure waste.

**Example policy:**

> Up to 3 attempts total, retrying only on connection errors, timeouts, 429, 502, 503, and 504. Use full-jitter exponential backoff with base 200 ms and cap 5 s, honoring `Retry-After`. Retries are limited to 10% of request volume per client. A circuit breaker opens at 50% errors over 20+ requests in 10 s, stays open for 30 s, then half-opens. No retries at inner layers.

The core idea is that retries should handle *transient, isolated* failures. When failures are *widespread*, the system should detect that and back off, not push harder.