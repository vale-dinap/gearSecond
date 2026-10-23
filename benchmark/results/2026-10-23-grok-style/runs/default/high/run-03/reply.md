Immediate retries turned one outage into a retry storm. Each failed call was sent again up to five times with no pause, so the dependency received up to six times its normal traffic while it was already failing. That extra load kept it from recovering, and the same pattern spread upstream.

**Why it got worse**

- **Load multiplied.** One user request became as many as six calls (the original plus five retries). With many callers, the dependency saw a sudden multiple of its usual QPS, more open connections, and deeper queues.
- **No time to recover.** The next attempt went out at once, while the service was still down or saturated. Recovery needs a drop in arrival rate; these retries removed that drop.
- **Retries lined up.** Callers that failed together retried together. The result was synchronized spikes, not a smooth trickle of retries.
- **Caller resources filled up too.** Each attempt held a connection, a thread, or a pool slot until it timed out. Five fast failures stacked that wait, so the caller’s own pools filled and it started failing its callers.
- **Timeouts duplicated work.** A timed-out request was often still running on the server. The retry added a second copy of the same work on a service that was already behind.

**Policy to use instead**

Retry only transient failures (connect errors, timeouts, 429, and 502/503/504). Leave 4xx and other deterministic errors alone. Cap retries at about two or three, and stop when a single overall deadline is exhausted so the caller still meets its own latency budget.

Space the attempts with exponential backoff and full jitter: wait `random(0, min(cap, base * 2^attempt))`, and honor `Retry-After` when the server sends it. Jitter keeps many clients from retrying on the same tick.

Put a circuit breaker in front of the dependency. After a run of failures, open the circuit and fail fast for a cool-down window, then let a few probes through. While it is open, send no retries.

Also cap how much of your traffic retries may be (a retry budget of around 10% of requests, or a token bucket). Retries then cannot multiply load without bound. Retry only idempotent calls, or send an idempotency key, so a second attempt does not apply the same side effect twice.

Backoff alone is not enough during a hard outage. The circuit breaker and the retry budget are what stop the callers from hammering a dependency that needs the traffic to stop.