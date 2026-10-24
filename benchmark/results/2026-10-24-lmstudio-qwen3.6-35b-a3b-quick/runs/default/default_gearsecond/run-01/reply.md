**Why it worsens the outage:**
- Multiplies traffic 5x per failed request, flooding a struggling dependency.
- Consumes connection pools, CPU, and memory across the stack before recovery.
- Delays recovery; load balancers and proxies may also exhaust resources.
- Triggers cascading failures in other services sharing infrastructure.

**Recommended retry policy:**
- Exponential backoff with jitter (e.g., 1s, 2s, 4s, 8s, 16s) to spread retries.
- Circuit breaker to halt retries after a failure threshold or timeout.
- Fixed max retries (3–5) paired with a strict request deadline/timeout.
- Dependency-level rate limiting to prevent overwhelming the target.
- Idempotency guarantees so duplicate requests don’t cause side effects.

This shifts retries from amplification to controlled, spaced attempts that let the dependency heal.