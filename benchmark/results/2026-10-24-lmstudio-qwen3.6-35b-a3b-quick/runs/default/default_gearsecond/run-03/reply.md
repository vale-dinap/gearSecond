**Why immediate retries worsen an outage**
- Each failure triggers 5 new requests instantly, multiplying load on a failing dependency.
- The dependency cannot recover while under artificial, concentrated traffic.
- Connection pools, thread pools, and memory exhaust faster, causing cascading failures.
- Clients waste time and resources on requests that will inevitably fail, delaying graceful degradation.

**Recommended retry policy**
Exponential backoff with jitter, bounded by a circuit breaker and per-request deadlines.

**Key configuration**
- Backoff: `base_time * 2^attempt` (e.g., 100ms → 200ms → 400ms → 800ms → 1600ms)
- Jitter: ±25% randomization to prevent synchronized retry storms across clients
- Max retries: 3–5 (match existing, but cap total wait time)
- Max total wait: ~30 seconds; stop retrying if exceeded
- Circuit breaker: trip after N consecutive failures; enter open state (drop requests); half-open tests recovery with limited probes
- Deadline propagation: inherit or set a strict timeout; cancel retry if deadline passes
- Rate limiting: cap outbound retry traffic per dependency to prevent cloud/provider throttling

**Why it works**
- Spreads retry load over time, giving the dependency a window to recover.
- Jitter prevents client synchronization from recreating the stampede.
- Circuit breaker stops amplifying the outage once failure is confirmed.
- Deadlines force early failure and fallback instead of futile retries.
- Rate limiting protects shared infrastructure and prevents cascading timeouts.