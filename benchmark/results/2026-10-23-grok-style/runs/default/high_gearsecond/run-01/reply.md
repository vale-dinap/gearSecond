Immediate retries turned one failed call into a burst of extra calls against a dependency that was already failing, so the dependency stayed overloaded and took longer to recover.

## Why it made the outage worse

Each caller retried up to five times with no delay. One user request became as many as six requests (the original plus five retries) in the same failure window. With many callers doing that at once, offered load jumped by about 6× exactly when the dependency could handle the least.

That has three effects:

- **No recovery window.** The dependency never gets a quiet interval to restart, finish garbage collection, drain a queue, or scale. Every failure is followed at once by more traffic.
- **Synchronized spikes.** Callers that fail together also retry together. The load arrives as a thundering herd instead of spreading out, so a brief blip becomes a sustained overload.
- **Resource pile-up on both sides.** Each retry holds a connection, a thread, and pool slots until it times out. Upstream callers then time out and retry too, so retries multiply across the call chain. Pools saturate, latency climbs, and healthy traffic gets crowded out by work that is going to fail anyway.

The dependency can look “down” long after the original fault is gone, because the retry traffic alone is enough to keep it saturated.

## Policy to use instead

Retry only transient failures on idempotent calls (timeouts, connection resets, 429, 503). Do not retry deterministic client errors. Bound every call with a per-try timeout and an overall deadline so the retry chain cannot outlive the caller’s budget.

Use **exponential backoff with full jitter**:

```text
sleep = random(0, min(cap, base * 2^attempt))
```

A typical start is a base around 100–200 ms, a cap of a few seconds, and at most 2–3 attempts. Jitter stops clients from lining up on the same timestamps. If the response includes `Retry-After`, wait at least that long.

Add two load limits so retries cannot multiply traffic without bound:

- **Retry budget.** Keep retries to a small fraction of total traffic (on the order of 10%). Once the budget is spent, fail fast instead of retrying.
- **Circuit breaker.** After a run of failures, open the circuit and stop calling for a cool-down. Then allow a few probe requests. If they succeed, close the circuit. If they fail, stay open. That sheds load while the dependency is down and lets it recover.

Together, backoff spreads the retries, the budget caps how much extra load you add, and the breaker stops calling a dependency that is not answering.