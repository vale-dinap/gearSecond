### Why Immediate Retries Made the Outage Worse

1. **Retry Storm / Thundering Herd Effect**  
   When a dependency fails, every client immediately fires 5 retries. If thousands of requests are pending, this instantly multiplies traffic by 5x (or more with concurrent calls). The failing dependency, already struggling, is flooded with synchronized load instead of being allowed to recover.

2. **Zero Delay = No Load Distribution**  
   Immediate retries mean all clients retry at the exact same millisecond. Instead of a manageable, distributed retry curve, you get a sharp spike that saturates network links, connection pools, and thread pools on both the client and server side.

3. **Resource Exhaustion on the Calling Service**  
   The service itself burns CPU, memory, and network connections managing these rapid retries. Threads block waiting for timeouts, connection pools exhaust, and the calling service may degrade or crash, turning a dependency outage into a broader system failure.

4. **Non-Idempotent Side Effects**  
   If the retried endpoint isn't strictly idempotent (e.g., `POST` creating records, `PUT` updating state), retries can duplicate work, corrupt data, or trigger cascading business logic failures.

5. **Prevents Dependency Recovery**  
   Failing services often need time to clear backlogs, scale up, or fail over. A retry storm starves them of capacity to do so, prolonging the outage and potentially triggering upstream circuit breakers or load balancer timeouts.

---

### Recommended Retry Policy

Replace immediate retries with a **bounded, randomized exponential backoff** strategy, combined with resilience patterns:

| Component | Recommendation | Why |
|-----------|----------------|-----|
| **Backoff Type** | Exponential + Jitter (e.g., `base_delay * 2^attempt + random(-30%, +30%)`) | Spreads retries over time; jitter prevents synchronized spikes |
| **Base Delay** | 100–500ms | Fast enough for transient glitches, slow enough to avoid amplification |
| **Max Delay Cap** | 5–10 seconds | Prevents unbounded waiting; balances urgency vs. safety |
| **Max Retries** | 3–4 (not 5) | Diminishing returns after 3; each retry costs resources |
| **Retry Budget** | Limit total retries per second/client (e.g., via token bucket or sliding window) | Prevents a single client from monopolizing retries |
| **Idempotency** | Only retry `GET`, `PUT`, `DELETE` (or use `X-Idempotency-Key` for `POST`) | Avoids duplicated state mutations |
| **Timeouts** | Tight, consistent timeouts (e.g., 1–3s) + connection timeouts | Fails fast; prevents thread/connection starvation |

**Example Policy:**
```
Attempt 1: 0s (initial call)
Attempt 2: 200ms ± 60ms
Attempt 3: 400ms ± 120ms
Attempt 4: 800ms ± 240ms
Attempt 5: 1.6s ± 480ms (stop here)
```

---

### Essential Complementary Patterns

1. **Circuit Breaker**  
   Stop retrying entirely after a threshold of consecutive failures (e.g., 50% error rate over 10s). Opens the circuit to let the dependency recover, then probes with lightweight health checks.

2. **Fallback / Degraded Mode**  
   Return cached data, default responses, or queue requests for async processing when the dependency is down. Never block the user experience unnecessarily.

3. **Observability**  
   Track `retry_count`, `retry_duration`, `circuit_breaker_state`, and `dependency_error_rate`. Alert on retry rate spikes before they become storms.

4. **Bulkhead Isolation**  
   Separate retry-heavy calls into independent thread pools/connection pools so one failing dependency doesn't starve healthy services.

---

### Key Takeaway
Retries are a tool for handling **transient** failures, not a substitute for proper dependency resilience. Immediate, unbounded retries amplify failures into system-wide outages. Use **bounded exponential backoff with jitter**, enforce **idempotency**, pair with a **circuit breaker**, and design for **graceful degradation**. This turns retries from a liability into a controlled safety net.