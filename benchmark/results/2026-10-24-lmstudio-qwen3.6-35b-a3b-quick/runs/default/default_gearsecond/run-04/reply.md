Immediate retries amplify the outage via a thundering herd effect. Each failure triggers another request, flooding a struggling dependency. This exhausts its connection pool, CPU, or memory, delaying recovery and potentially cascading failures. It also wastes client resources on doomed requests.

Use this policy instead:
- **Exponential backoff with jitter:** Start with a short delay (e.g., 100–500ms) and double it each retry. Add random variance to prevent synchronized bursts.
- **Hard limit:** Cap retries at 3. Five usually harms more than helps.
- **Circuit breaker:** Stop retrying after N consecutive failures (e.g., 5 in 30s). Fail fast until the dependency recovers.
- **Idempotency guard:** Only retry idempotent methods (GET, PUT, DELETE). Never retry POST or non-idempotent writes.
- **Honor `Retry-After` headers:** If the dependency specifies a wait time, respect it.

This reduces load on the failing service, speeds recovery, and isolates failure.