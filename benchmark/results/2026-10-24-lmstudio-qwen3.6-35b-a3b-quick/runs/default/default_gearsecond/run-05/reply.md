**Why immediate retries worsened the outage:**
- Creates a retry storm: all failed requests hit the dependency simultaneously.
- No cooling-off period prevents the dependency from scaling or healing.
- Load spikes exhaust server resources (CPU, threads, connections, memory).
- Wastes client resources (thread pools, memory, bandwidth).
- Extends outage duration by overwhelming recovery capacity.

**Recommended retry policy:**
- **Exponential backoff with jitter:** `delay = min(base * 2^attempt + random(0, jitter), max_delay)`
- **Circuit breaker:** Stop retrying after a failure threshold (e.g., 5 consecutive failures). Fail fast until dependency recovers.
- **Capped max retries:** 3–5 attempts. Additional retries rarely succeed during outages.
- **Max delay cap:** 30–60 seconds. Prevents excessive client wait times.
- **Health-aware routing:** Check dependency status/health endpoint before retrying; skip retries if known down.

**Key implementation details:**
- Jitter desynchronizes retries from other clients, preventing synchronized load spikes.
- Circuit breaker trips immediately on consistent failure; resets after a cooldown + health check.
- Log retry attempts and dependency latency; alert on circuit breaker trips.
- Pair with rate limiting to protect downstream systems during recovery.