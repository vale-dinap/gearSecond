Immediate retries multiplied the load on a dependency that was already failing, so it could not recover.

Each user request became up to six calls (the original plus five retries). During the outage those calls failed fast and were reissued at once, so traffic to the dependency jumped by as much as 6×. Every client hit the same failure at the same moment and retried together, which produced synchronized bursts instead of a pause. The dependency stayed saturated: connection queues, thread pools, and CPU never had a quiet interval in which to drain and come back.

The caller suffered too. Each attempt held a connection, a thread, or a request slot until it failed. Six back-to-back attempts stretched that hold and exhausted the caller’s pools, so latency and failures spread upstream even for work that did not need the sick dependency.

Use a policy that retries rarely, waits longer between tries, and stops calling once the dependency is clearly down:

- **Retry only transient failures.** Retry timeouts, connection errors, and 408, 429, and 5xx responses that mean “try later.” Do not retry other 4xx responses. Retry a non-idempotent call only when it carries an idempotency key.
- **Exponential backoff with full jitter.** For example, wait `random(0, min(cap, base * 2^attempt))` — something like 100 ms base, 2–3 s cap — so clients do not retry in lockstep. If the response has `Retry-After`, wait at least that long.
- **Small attempt budget and a hard deadline.** Allow about two or three attempts, and abandon the call when the overall deadline is hit even if attempts remain. That caps amplification at roughly 2–3× and bounds how long resources stay occupied.
- **Circuit breaker.** After a run of failures or a high error rate, open the circuit and fail fast for a cooldown (tens of seconds). Then allow a few probe requests. While the circuit is open, send no retries.
- **Cap in-flight work.** Limit concurrent calls and retries to that dependency (a bulkhead) so a sick dependency cannot consume the whole process.

Together, backoff spreads the remaining retries, the deadline and attempt cap bound the extra load, and the circuit breaker removes that load for the rest of the outage so the dependency can recover.