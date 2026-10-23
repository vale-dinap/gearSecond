Immediate retries multiply load on a dependency that is already failing, so the outage lasts longer and spreads.

## Why it makes the outage worse

Each caller request becomes up to six calls (the original plus five retries) with no pause between them. While the dependency is down or overloaded, that extra traffic does not help. It consumes the dependency’s remaining connections, threads, and CPU, and it fills its queues.

Callers pay the same cost. Threads and connection pools stay busy on calls that will fail, so the service slows down for work that does not even need that dependency.

When the dependency starts to recover, every caller retries at once. That synchronized burst can knock it over again. A short blip becomes a longer outage, and the failure cascades upstream.

Retries also fire on errors that will not succeed on the next try (most 4xx responses, bad payloads). Those attempts only add load.

## Policy to use instead

Retry only transient failures: connection errors, timeouts, HTTP 429, and 503. Skip other 4xx responses. Retry only idempotent calls, or send an idempotency key.

Use exponential backoff with full jitter, and cap both the number of attempts and the total time:

- Attempt 1: no delay
- Later attempts: wait `random(0, min(cap, base * 2^attempt))`, for example base 100 ms, cap 2–5 s, at most 3 retries
- Stop when a deadline or retry budget is exhausted
- If the response has `Retry-After`, wait at least that long

Add a circuit breaker. After a run of failures, open the circuit and fail fast for a cool-down period instead of calling the dependency. Probe with a few requests before closing it again. Limit concurrent in-flight calls (a bulkhead) so one dependency cannot exhaust the process.

The dependency then sees a smaller, spread-out load and has room to recover. Callers fail quickly when it is down, and they come back gradually when it returns.