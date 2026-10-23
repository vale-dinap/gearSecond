Immediate retries turn one outage into a larger one. Each failed call becomes up to six attempts in a row, all aimed at a dependency that is already failing or overloaded. Callers stay in lockstep, so the extra traffic arrives as a spike instead of spreading out. That spike keeps the dependency from recovering, ties up the caller’s threads and connections, and pushes the failure upstream.

Use a bounded retry policy with backoff, jitter, and a circuit breaker.

- **Retry only transient failures** on idempotent calls: connection errors, timeouts, 429, and 503. Honor `Retry-After` when the server sends it.
- **Exponential backoff with full jitter.** For example, wait a random time between 0 and `min(cap, base * 2^attempt)` before each retry, with a base around 100–200 ms and a cap around 5–30 s. Jitter stops every client from retrying on the same schedule.
- **Cap both attempts and total time.** Three retries is usually enough, and stop once the caller’s deadline is too close for another attempt to finish.
- **Add a retry budget.** Allow only a small fraction of extra calls, such as 10% above normal traffic, so retries cannot multiply load during a wide outage.
- **Open a circuit breaker** when the error rate stays high. Fail fast for a cool-down period, then send a few probe requests. Resume normal calls only after those probes succeed.

Backoff alone still sends extra load. The budget and the circuit breaker are what stop the caller from making the outage worse.