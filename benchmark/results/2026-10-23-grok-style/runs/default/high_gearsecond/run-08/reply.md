Immediate retries turned one outage into a larger one. Each caller multiplied its load on a dependency that was already failing, and every caller did it at the same moment.

## Why it got worse

During the outage, almost every call failed. The service then issued up to five more calls with no pause, so one user request became as many as six requests against the same broken dependency. That extra traffic is what kept the dependency from recovering: connection pools, threads, and CPU on both sides stayed saturated with work that was going to fail anyway.

Because the retries were immediate and shared the same trigger, they also lined up. When the dependency started to accept traffic again, every caller retried together and knocked it back over. That is a retry storm. Meanwhile the caller held sockets and worker threads for the whole retry sequence, so its own latency and queue depth rose and the failure spread upstream.

## Policy to use instead

Retry only transient failures (timeouts, connection resets, `429`, `503`), and only when the operation is safe to repeat or carries an idempotency key. Cap both the attempt count and the total time spent retrying, and keep each attempt inside the caller’s overall deadline.

Space the attempts with exponential backoff plus full jitter, and honor `Retry-After` when the dependency sends it. A typical shape is a small base delay (for example 100 ms), doubling each time, with the wait drawn at random between zero and that delay, and a ceiling around a few seconds. Jitter stops the callers from lining up again.

Add a circuit breaker around the dependency. After a sustained error rate, stop calling, fail fast, and send only occasional probes until success returns. Limit how many calls and retries can be in flight at once so a sick dependency cannot exhaust the caller’s pools.

The goal is fewer calls while the dependency is down, spread out in time, and cut off entirely once it is clear that more attempts will not help.