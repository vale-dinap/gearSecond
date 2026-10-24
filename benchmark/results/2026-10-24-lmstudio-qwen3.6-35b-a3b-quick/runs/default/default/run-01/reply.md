### Why Immediate Retries Worsen an Outage

When a dependency fails, immediately retrying up to 5 times triggers a **retry storm** (also called a thundering herd or retry avalanche). Here’s how it amplifies the outage:

1. **Load Amplification**: Each failed request instantly spawns 5 more. If 1,000 clients hit the failure, you suddenly generate ~6,000 requests targeting a system that’s already struggling.
2. **Resource Exhaustion**: The failing dependency is likely already depleted (threads, connections, CPU, memory, or rate limits). Retry traffic consumes the same scarce resources, pushing it past the breaking point.
3. **Delayed Recovery**: Systems often recover faster when load drops. Retry storms keep the dependency pinned at high utilization, preventing it from draining its backlog or healing.
4. **Cascading Multipliers**: If the dependency also retries, the storm compounds across services. Connection pools, load balancers, or databases may hit hard limits, causing secondary failures.
5. **Wasted Resources**: Retries during a systemic outage are almost always futile. They burn CPU, network bandwidth, and money without increasing success probability.

---

### Recommended Retry Policy

Replace immediate retries with a **resilient, adaptive retry strategy**:

| Principle | Recommendation |
|-----------|----------------|
| **Exponential Backoff** | Start with a base delay (e.g., `100ms–1s`), multiply by `2` each retry: `100ms → 200ms → 400ms → 800ms → 1.6s`. This gives the dependency time to recover. |
| **Jitter** | Add randomization to desynchronize clients: `delay × (0.5 + random(0, 0.5))`. Prevents synchronized retry spikes. |
| **Retry Only on Transient Errors** | Retry on: `5xx` status codes, `429 Too Many Requests`, timeouts, DNS/connection failures. **Never** retry `4xx` (except `429`), auth errors, or validation failures. |
| **Circuit Breaker** | Stop retrying after a threshold (e.g., `5 consecutive failures` or `>50% error rate` in a `10s` window). Open the circuit for `30–60s` to let the dependency heal. |
| **Retry Budget / Deadline** | Limit total retries to `3` or cap retry time at `5–10s`. Use the `Retry-After` header if provided by the dependency. |
| **Idempotency Awareness** | Only retry `GET`, `PUT`, `DELETE`, or idempotent `POST`. For non-idempotent calls, use idempotency keys or queue the work instead of retrying. |
| **Queue for Non-Critical Work** | Decouple with a message queue (SQS, RabbitMQ, Kafka). Process with backpressure and automatic retries instead of inline retries. |

---

### Implementation & Monitoring Tips

- **Use battle-tested libraries**: `resilience4j` (Java), `Polly` (.NET), `retry`/`circuitbreaker` (Python), `go-retry` (Go), or cloud-native service mesh policies (Istio, Envoy).
- **Log & metric retries**: Track retry count, delay, success/failure rate, and error types. Alert on sudden retry volume spikes.
- **Tune per dependency**: Critical, fast-recovering services may tolerate shorter backoffs. Slow or rate-limited services need longer delays and stricter circuit breakers.
- **Graceful degradation**: When the circuit opens, return cached data, fallback responses, or `503` with a clear message instead of failing hard.

---

### Key Takeaway
Immediate retries assume failures are **transient and isolated**. During an outage, failures are **systemic and synchronized**. Exponential backoff + jitter + circuit breaking + error filtering transforms retries from an amplification vector into a controlled, recovery-friendly mechanism. Always design retries with the dependency’s capacity and recovery trajectory in mind.