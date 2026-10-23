Immediate retries turned a dependency outage into a larger one by multiplying load on a service that was already failing.

Each failed call became up to five calls in a row, with no pause. While the dependency was slow or down, those extra attempts piled onto the same saturated threads, connection pools, and queues. Callers that failed together retried together, so the spikes lined up. Each attempt also held a connection until it timed out, so in-flight work and tail latency grew with every retry. The dependency never got a quiet interval in which to recover, and the failure spread upstream.

Use a bounded retry policy with exponential backoff and jitter, and stop calling altogether when the dependency is clearly down.

- Retry only transient failures: connection errors, timeouts, `429`, `502`, `503`, and `504`. Honor `Retry-After` when the server sends it.
- Wait between attempts. A typical schedule is about 100 ms, 200 ms, 400 ms, 800 ms, then stop, with full jitter so clients do not retry on the same tick. Cap the delay and the number of attempts (often 2–3, inside one overall deadline).
- Keep a retry budget, for example retries as a small fraction of normal traffic, so retries cannot multiply load by five.
- Open a circuit breaker after repeated failures and fail fast until a probe succeeds.
- Send an idempotency key on any non-safe method so a retried call does not apply twice.