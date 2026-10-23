Immediate retries turn one failed call into a burst of calls against a dependency that is already failing. That extra traffic is what deepens the outage.

## Why immediate retries make it worse

Suppose the dependency starts returning errors or timing out. Every caller that would have sent **1** request now sends **6** (the original plus 5 retries), back to back. Across many callers that fail at the same moment, that is a retry storm:

- **Load multiplies on the thing that is already down.** A service at capacity, restarting, or shedding load gets several times the traffic just as it most needs less. Queues, thread pools, and connection pools stay full, so it cannot recover.
- **The retries are synchronized.** Callers that failed together retry together, with no gap. The dependency sees a stampede instead of a trickle it could drain.
- **Latency and resources stack on the caller.** Each attempt holds a connection and often waits out a full timeout. Five immediate attempts can turn a 1-second failure into many seconds of occupied threads and sockets. Upstream callers then time out and retry too, and the failure spreads.
- **Non-transient errors get the same treatment.** A 400 or 404 is retried as hard as a 503, which wastes capacity and does nothing to help the outage.

## Policy to use instead

Use a capped, jittered backoff, and stop calling altogether when the dependency is clearly down.

1. **Exponential backoff with full jitter.** After attempt `n`, wait a random duration in `[0, min(cap, base × 2^n)]` — for example base 100 ms, cap 2–5 s. The exponential growth leaves a recovery window. The random draw keeps callers from retrying in lockstep.
2. **A small budget and a deadline.** For example at most 3 attempts, and stop when the total time for the call hits a budget such as 1–2 s. The deadline matters more than the attempt count: it keeps one user request from occupying a thread for the sum of every timeout.
3. **Retry only transient failures.** Connection errors, timeouts, and 408, 429, 502, 503, 504. Honor `Retry-After` when it is present. Do not retry other 4xx responses.
4. **A circuit breaker on that dependency.** After a run of failures, open the circuit and fail fast for a cool-down (for example 10–30 s). Then let a few probe requests through. While the circuit is open, this service stops adding load, which is what lets the dependency come back.
5. **A bulkhead.** Cap in-flight calls and retries to that dependency so a burst cannot take every thread and connection in the process.
6. **Idempotency.** Retry only safe or idempotent operations, or send an idempotency key, so a retry cannot apply a side effect twice.

Backoff alone is not enough during a long outage: callers still converge on the dependency, just more slowly. The circuit breaker is what cuts the amplification off.