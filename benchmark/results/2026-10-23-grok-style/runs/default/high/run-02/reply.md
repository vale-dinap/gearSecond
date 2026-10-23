Immediate retries multiplied traffic into a dependency that was already failing, so the outage lasted longer and spread.

Each failed call became up to six attempts in a tight burst (the original call plus five retries). With no delay, those attempts landed while the dependency was still down or overloaded. Across many callers that failed at the same time, the bursts lined up. A service that was struggling with 1x load suddenly saw about 6x, often on the same saturated threads, connection pools, and CPU. That extra work produces more timeouts, which produce more retries. The dependency cannot shed load and recover, queues grow, and upstream callers start timing out and retrying too.

A better policy fails fast when the dependency is unhealthy, and retries only transient errors with a capped, jittered backoff:

- **Retry only transient failures.** Retry connection resets, timeouts, HTTP 429, and 502/503/504. Do not retry 400, 401, 403, 404, or other client errors. Retry a non-idempotent write only when the call carries an idempotency key.
- **Exponential backoff with full jitter and a cap.** For example, wait `random(0, min(cap, 100ms * 2^attempt))`, with the cap around 2–5 seconds. Jitter keeps many clients from retrying on the same tick. Honor `Retry-After` when the server sends it.
- **Few attempts inside one deadline.** Use about three attempts total, and stop when the remaining time is less than the next wait plus a reasonable timeout. A caller with a 1-second budget should not spend several seconds retrying.
- **A circuit breaker around the client.** After a short run of consecutive failures, open the circuit and fail immediately for a cool-down (for example 10–30 seconds). Then allow a few probe calls. If they succeed, close the circuit. While it is open, callers get a fast error instead of adding load.
- **Bound in-flight work.** Cap concurrent calls and retries to that dependency (a bulkhead or adaptive limit) so a retry loop cannot exhaust the caller’s own threads and connections.

The dependency then sees a smaller, spread-out trickle of retries and long quiet gaps in which it can recover, and the caller spends its time failing fast instead of amplifying the outage.