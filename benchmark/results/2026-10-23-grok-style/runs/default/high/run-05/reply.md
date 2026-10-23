Immediate retries multiply load on a dependency that is already failing, so the outage lasts longer and spreads.

## Why this made the outage worse

Each caller request becomes up to six requests in a tight loop: the original call plus five retries, all issued as soon as the previous one fails. During an outage that load does not help. The dependency is already slow or rejecting work, and the extra calls arrive while it is still down.

That amplification shows up in a few ways:

- **More traffic on the failing service.** If a thousand callers each retry five times at once, the dependency sees about six thousand attempts instead of one thousand. Threads, connections, and CPU stay saturated, so it cannot drain its queue or restart cleanly.
- **No time to recover.** An immediate retry hits the same overloaded process before it has shed load, restarted, or failed over. Recovery needs a drop in arrival rate. This policy never gives it one.
- **Synchronized retries.** Every caller fails at roughly the same moment and retries at roughly the same moment. The dependency sees waves of traffic instead of a steady rate, which is the thundering-herd pattern.
- **The caller fails too.** Each retry holds a connection, a thread, and a timeout budget. Under the outage the caller exhausts its own pools, so healthy requests start failing as well. Upstream services then retry those failures, and the storm moves one tier out.
- **Retries of errors that will never succeed.** A tight loop also replays 400s, 401s, and 404s, which wastes capacity on calls that cannot succeed.

## Retry policy to use instead

Retry only when another attempt might succeed, wait longer between attempts, and stop calling once the dependency is clearly down.

- **Retry only transient failures:** connection errors, timeouts, HTTP 429, and HTTP 503. Honor `Retry-After` when the server sends it. Do not retry other 4xx responses. Retry only idempotent calls, or calls that carry an idempotency key.
- **Exponential backoff with full jitter.** For example, wait a random time between 0 and `min(cap, base * 2^attempt)` — something like base 100 ms, cap 5–10 s. Jitter keeps callers from retrying in lockstep. Cap the number of attempts (often 2–3, not 5) and also cap total elapsed time so a request cannot outlive its deadline.
- **A circuit breaker around the client.** After the error rate or consecutive failures cross a threshold, open the circuit and fail fast for a cool-down period. Then allow a few probe calls. If those succeed, close the circuit. While it is open, the dependency gets a real pause and the caller stops spending threads on a dead dependency.
- **Budgets and isolation.** Bound in-flight calls and retries per dependency (a bulkhead) so one outage cannot take the whole process. Pass the remaining deadline downstream and make each attempt’s timeout shorter than that deadline.

The goal is fewer calls when the dependency is unhealthy, spaced out so they do not arrive together, and a hard stop when retries are no longer useful.