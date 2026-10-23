## Why immediate retries made the outage worse

**1. Load amplification.** Each logical request can become up to 6 HTTP calls (1 original + 5 retries). When the dependency starts failing, almost every request hits the retry path, so traffic to an already-struggling service jumps by up to **6x** at the worst moment. If several layers each retry (A→B→C, each retrying 5x), the multiplication compounds: 6 × 6 = 36x at the bottom.

**2. No time to recover.** Immediate retries arrive within milliseconds, while the cause (overload, GC pauses, a restarting pod, exhausted connection pool) is still present. They are nearly guaranteed to fail and just add queue depth.

**3. Synchronization (thundering herd).** Every client that saw the failure retries at the same instant, so load comes in correlated spikes instead of being spread out. When the dependency briefly recovers, it gets hit by a wall of pent-up retries and falls over again. This creates a **metastable failure**: the original trigger is gone, but retry traffic alone keeps the system down.

**4. Retrying non-transient errors.** If the policy retries everything (400s, auth failures, timeouts on non-idempotent calls), it wastes capacity and can cause duplicate side effects.

**5. Resource exhaustion on the caller.** Threads, sockets, and memory are held through all 6 attempts, so the calling service degrades too, and the failure spreads upstream.

## A better retry policy

**Exponential backoff with jitter.** Wait `base * 2^attempt`, capped, and randomize it. "Full jitter" works well:
```
sleep = random(0, min(cap, base * 2^attempt))
# e.g. base=100ms, cap=10s
```
Backoff gives the dependency time to recover. Jitter de-synchronizes clients.

**Fewer attempts.** 2–3 retries is usually enough. Beyond that you are mostly adding load, not success rate.

**Retry only what is retryable.**
- Retry: connection errors, 502/503/504, 429, timeouts, but only on **idempotent** operations (or with idempotency keys).
- Don't retry: 4xx client errors (other than 408/429), validation and auth failures.
- Honor `Retry-After` headers.

**Retry budget.** Limit retries to a fraction of traffic, e.g. retries ≤ 10% of requests over a sliding window (the token-bucket approach used by gRPC and Finagle). During a healthy period this is invisible. During an outage it caps amplification at about 1.1x instead of 6x. This is the single most important fix.

**Circuit breaker.** After the error rate crosses a threshold, open the circuit and fail fast (or serve a fallback or cached response) for a cooldown period, then let a few probe requests through (half-open) before resuming. This removes load from the dependency entirely while it is down.

**Deadlines, not just attempt counts.** Give the whole operation a total time budget and propagate it downstream. Don't start a retry that can't finish before the caller's deadline.

**Retry at one layer only.** In a call chain, retry at a single layer (usually the one closest to the user or the edge), and have inner layers fail fast, to avoid multiplicative amplification.

### Example policy
```
max_attempts:     3 (1 original + 2 retries)
backoff:          exponential, base 100ms, cap 5s, full jitter
retry_on:         connect errors, timeouts, 502/503/504, 429 (honor Retry-After)
idempotent_only:  true (or require idempotency key)
retry_budget:     retries ≤ 10% of requests, min 10 retries/sec
circuit_breaker:  open at ≥50% errors over 20+ requests in 10s; 30s cooldown; half-open probes
overall_deadline: propagated from caller
```

In short, the original policy turned failures into extra load. The replacement backs off, spreads retries out, caps total retry volume, and stops calling a dependency that is clearly down.