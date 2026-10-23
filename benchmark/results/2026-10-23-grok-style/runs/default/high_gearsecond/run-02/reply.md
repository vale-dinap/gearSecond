Immediate retries multiplied the load on a dependency that was already failing, so the outage spread instead of clearing.

Each failed call became up to six calls in a row (the original plus five retries), all at once. During an outage many callers fail together, so those bursts line up: a service that was struggling suddenly sees several times its normal traffic, with no pause in which to recover. Threads, connection pools, and queues stay full on both sides, latency climbs, and more callers start failing and retrying. A partial outage turns into a retry storm.

Use a policy that retries less, later, and only while the dependency still looks healthy:

- **Retry only transient failures.** Connection errors, timeouts, and 429/502/503/504 are worth another try. A 4xx that means the request itself is wrong should fail immediately. Retry only idempotent calls, or ones you can safely repeat.
- **Exponential backoff with jitter.** Wait something like `random(0, base * 2^attempt)` between tries (full jitter), and honor `Retry-After` when the server sends it. Jitter keeps every client from retrying on the same tick.
- **A short budget.** Cap attempts (often 2–3) and cap total time spent retrying so one call cannot hold a thread for the whole outage.
- **A circuit breaker.** After a run of failures, stop calling for a cool-down, then send a few probes. While the circuit is open, fail fast. That removes the extra load until the dependency is actually answering again.
- **A concurrency limit** on in-flight calls to that dependency, so retries cannot consume the whole client.