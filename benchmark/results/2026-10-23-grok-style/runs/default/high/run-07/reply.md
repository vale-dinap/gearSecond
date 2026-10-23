Immediate retries multiply load on a dependency that is already failing, so the outage lasts longer and spreads.

## Why it gets worse

Each caller request becomes up to six calls (the original plus five retries). If many callers hit the outage at once, they all retry at the same moment. That is a retry storm: the dependency sees a burst several times larger than normal traffic exactly when it cannot keep up.

Immediate retries also give the dependency no quiet interval in which to recover. Threads, connection pools, and CPU stay saturated on both sides. Queues grow, timeouts pile up, and the calling service itself slows down. Its own callers then time out and retry, so the extra load cascades upstream.

Retries during an outage are also mostly useless. A process that is down, overloaded, or restarting is still down a few milliseconds later. The extra attempts fail the same way and only add work.

## Policy to use instead

Retry only when the call is safe to repeat and the error looks transient: connection failures, timeouts, HTTP 429, and HTTP 503. Do not retry other 4xx responses.

Use **exponential backoff with full jitter**, and cap both the attempt count and the total time:

- Wait `random(0, min(cap, base * 2^attempt))` before each retry. A typical start is a base of about 100 ms, a cap around 5–30 seconds, and at most 3 retries.
- Stop when a per-request deadline is reached, even if attempts remain. That deadline should be shorter than the caller’s own timeout.
- Honor a `Retry-After` header when the dependency sends one.
- Put a **circuit breaker** in front of the dependency. After a run of failures, fail fast and send only occasional probes until it recovers. Limit how many retries can be in flight so they cannot fill the thread pool or connection pool.

Backoff spreads retries out in time. Jitter stops clients from lining up on the same delays. The circuit breaker stops calling a dependency that is clearly down, which is what lets it recover.