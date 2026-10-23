Immediate retries turned one outage into a larger one because every failed call became up to six calls in a row, all aimed at a dependency that was already failing.

While the dependency is down or slow, each caller keeps the connection, thread, and timeout budget occupied and then fires the next attempt at once. With many callers doing that together, offered load jumps by about 6× (1 try + 5 retries) at the worst moment. The extra traffic fills connection pools and request queues, so requests that might have succeeded are dropped or time out, which triggers still more retries. Recovery gets harder: the dependency cannot shed load or restart cleanly while that amplified traffic keeps arriving. Because the retries are immediate and unsynchronized only by chance, they also tend to line up, so the dependency sees bursts instead of a smooth trickle.

Use a bounded retry policy that backs off, spreads attempts out, and stops calling once the dependency is clearly down:

- **Retry only transient failures.** Retry timeouts, connection resets, and 429/502/503/504. Do not retry other 4xx responses or non-idempotent calls unless the operation is safe to repeat.
- **Exponential backoff with full jitter.** For attempt `n` (starting at 0), wait `random(0, min(cap, base * 2^n))`, for example base 100 ms, cap 5–10 s. Jitter keeps callers from retrying in lockstep.
- **Honor `Retry-After`.** When the dependency sends it, wait at least that long.
- **Cap by a deadline, not only by count.** Allow a few attempts, but stop when the caller’s remaining time budget is gone so a slow dependency cannot pin threads for the whole retry sequence.
- **Open a circuit breaker.** After a run of failures, stop sending traffic for a cool-down, then allow a few probe requests. If those fail, stay open. That removes the amplification while the outage continues.
- **Limit in-flight calls** to the dependency (a small pool or concurrency cap) so retries cannot exhaust local threads and connections.

Together, backoff plus jitter lowers and spreads the extra load, and the circuit breaker stops the retry loop from feeding the outage.