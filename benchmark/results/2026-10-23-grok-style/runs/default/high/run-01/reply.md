Immediate retries multiplied load on a dependency that was already failing, so it could not recover.

Each caller turned one failed call into as many as six (the original plus five retries) in a tight loop. While the dependency was down, those retries all failed too, but they still consumed connections, threads, and CPU on both sides. Callers that failed together retried together, so the extra traffic arrived as synchronized bursts. When the dependency started to come back, that burst often pushed it over capacity again. In-flight work also piled up: each logical call waited through several timeouts, so the caller exhausted its own pools and the outage spread upstream.

Use a bounded policy that fails fast once the dependency is clearly unhealthy:

- Retry only transient failures (timeouts, connection resets, 429, 503), and only idempotent calls or ones protected by an idempotency key. Honor `Retry-After` when it is present.
- Cap attempts at about three total, with a per-try timeout and an overall deadline. Skip another try if the deadline cannot fit it.
- Wait with exponential backoff and full jitter: `sleep = random(0, min(cap, base * 2^attempt))`, with a cap of a few seconds. Jitter keeps callers from retrying in lockstep.
- Limit amplification with a retry budget (for example, retries stay under about 10% of recent calls). Past that budget, fail immediately.
- Open a circuit breaker after a sustained error rate, fail fast during a cool-down, then send a few probes before closing the circuit.

That keeps a short blip recoverable and stops an outage from being multiplied by every client.