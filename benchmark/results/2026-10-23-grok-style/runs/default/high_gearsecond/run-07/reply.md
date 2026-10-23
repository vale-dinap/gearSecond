Immediate retries turned one failed call into a burst of extra load on a dependency that was already failing, so the outage lasted longer and spread further.

## Why it made the outage worse

Each user request became up to six requests (the original call plus five retries), all sent with no pause. During an outage that multiplies traffic at the worst moment:

- The dependency is already slow or erroring. Extra calls fill its queues, saturate threads and connections, and drive latency up, so more calls time out and retry.
- Callers pile on together. When the dependency blips, every client retries at once. That synchronized spike is a retry storm: recovery starts, the burst knocks it over again, and the outage stretches.
- The caller suffers too. Holding five extra attempts per request ties up its own connection pool, threads, and memory, so a downstream outage becomes an upstream one.
- A fixed cap of five does not limit damage if many callers each send all five immediately. The limit is per call, not on aggregate load.

## Policy to use instead

Retry only calls that are safe to repeat (idempotent methods, or requests with an idempotency key) and only for transient failures: connection errors, timeouts, and 408, 429, and 5xx responses. Do not retry other 4xx responses.

Use exponential backoff with full jitter, and a hard deadline for the whole operation:

- Wait `random(0, min(cap, base * 2^attempt))` before each retry (for example base 100 ms, cap 2–5 s).
- Allow a small number of attempts (about 3) and stop when the overall deadline is reached, even if attempts remain.
- Honor `Retry-After` on 429 and 503.

Pair that with a circuit breaker. After a run of failures, open the circuit and fail fast for a cool-down, then let a few probes through. While the circuit is open, callers shed load instead of hammering the dependency. A client-side concurrency limit or retry budget (only a fraction of calls may be retries) keeps aggregate retry traffic bounded even when many requests fail at once.

That gives the dependency quiet time to recover, spreads retries so they do not land together, and stops the caller from spending its own resources on calls that are not going to succeed.