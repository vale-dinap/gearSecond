### Why Immediate Retries Worsened the Outage

1. **Request Amplification**  
   Every failed request triggers up to 5 additional requests. If your service receives `N` incoming requests, the dependency suddenly sees up to `5N` requests. This multiplier effect can easily overwhelm a struggling dependency.

2. **No Cooling-Off Period**  
   Immediate retries hit the dependency in rapid succession, often while it's still recovering or saturated. Without delays, retries compete with legitimate traffic for the same scarce resources (CPU, connections, memory, disk I/O).

3. **Resource Exhaustion in the Calling Service**  
   Threads, connection pools, or async workers in your service get blocked waiting for retry timeouts. This starves legitimate work, increases p99 latency, and can cause cascading failures (e.g., thread pool exhaustion, OOM, or gateway timeouts).

4. **Prevents Dependency Recovery**  
   A failing service often needs reduced load to clear queues, release locks, or recover state. Constant retry traffic keeps it in a failure loop, extending the outage duration.

5. **Thundering Herd Risk**  
   If retries are scheduled or queued without jitter, they may all fire simultaneously when the dependency comes back online, causing a secondary spike that triggers another failure window.

---

### Recommended Retry Policy

A production-grade retry strategy should be **bounded, adaptive, and observant**. Here’s what to implement instead:

| Principle | Why It Matters | Typical Configuration |
|-----------|----------------|------------------------|
| **Exponential Backoff** | Spreads retries over time, giving the dependency room to recover | `base_delay × 2^attempt` (e.g., 1s, 2s, 4s, 8s, 16s) |
| **Jitter** | Prevents synchronized retry storms across clients | Add ±20–50% random variation to each delay |
| **Circuit Breaker** | Stops retrying when the dependency is clearly down, preventing resource exhaustion | Open circuit after `X` failures in `Y` seconds; half-open after `Z` seconds |
| **Error-Code Awareness** | Only retry recoverable errors, not client errors | Retry on: `5xx`, `429`, timeouts, network errors. **Never** retry `4xx` (except `429`) |
| **Idempotency Requirement** | Retrying non-idempotent requests can cause duplicate state changes | Only retry GET, PUT, DELETE, or idempotent POSTs; require explicit confirmation for others |
| **Strict Timeouts** | Prevents threads/pools from being held indefinitely | Per-request timeout ≤ retry budget (e.g., 2s timeout, 10s max retry window) |
| **Observability & Alerts** | Detect retry storms before they cascade | Log retry counts, track circuit breaker state, alert on retry rate > threshold |

#### Example Policy (Conceptual)
```text
Max retries: 3
Backoff: exponential, base 1s
Jitter: ±30%
Max total retry duration: 30s
Retry only on: 5xx, 429, network timeout, connection reset
Circuit breaker: open after 50% failures over 10s, half-open after 30s
Timeout: 2s per attempt
Idempotent only: yes (or require explicit flag)
```

---

### Implementation Notes
- Use battle-tested libraries: `Polly` (.NET), `Resilience4j` (Java), `tenacity` (Python), `retry`/`backoff` (Go/Node), or service mesh policies (Istio, Linkerd).
- **Never retry without a circuit breaker** in distributed systems. They are complementary, not optional.
- Monitor **retry-to-success ratio**, **retry latency**, and **circuit breaker state**. High retry rates are a symptom, not a solution.
- If the dependency is down, fail fast and degrade gracefully (cache fallback, queued processing, or user-facing error) rather than burning resources on retries.

This approach turns retries from a cascade trigger into a resilience mechanism, preserving system stability during partial failures.