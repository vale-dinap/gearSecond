Immediate retries multiplied the load on a dependency that was already failing, so it never got a quiet interval in which to recover.

Each failed call became up to six calls in a row (the original plus five retries), all issued at once. During an outage every caller does this together, so traffic jumps by roughly that factor and arrives as a synchronized burst. The dependency spends its remaining capacity on work that will fail again. Timeouts keep connections and threads occupied, queues grow, latency rises, more calls time out, and those time out into still more retries. That feedback loop is what turns a partial outage into a longer, wider one. The same pattern hits the caller: its own connection pool and thread pool fill with in-flight retries, so unrelated work stalls too.

Use a policy that spends less traffic the worse the dependency looks:

- Retry only transient failures: connection errors, timeouts, and 429/502/503. Skip client errors such as 400 and 404. Retry only operations that are safe to repeat, or send an idempotency key.
- Wait between attempts with exponential backoff and full jitter: `sleep = random(0, min(cap, base * 2^attempt))`, with a cap of a few seconds. Jitter keeps callers from retrying in lockstep.
- Cap total attempts and total time. A deadline of a couple of seconds with at most 2–3 retries is enough for a blip. If the remaining deadline is shorter than the next backoff plus timeout, stop and fail.
- Honor `Retry-After` when the server sends it.
- Open a circuit breaker after a run of failures. While it is open, fail immediately and send no traffic. After a cool-down, allow a few probe calls; close the circuit only if those succeed.
- Bound in-flight calls with a concurrency limit so retries cannot exhaust the caller’s own pools.

Backoff spreads the retries that are still worth making. The circuit breaker is what stops the amplification once the dependency is actually down.