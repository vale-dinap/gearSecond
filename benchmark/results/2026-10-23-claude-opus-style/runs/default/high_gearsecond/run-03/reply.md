## Why immediate retries made it worse

**Load amplification.** Each failing request becomes up to 6 requests (1 original + 5 retries). When the dependency is already overloaded, it now receives up to 6x the traffic at exactly the moment it can least handle it. Requests that would have failed once now fail six times, each consuming connections, threads, and CPU on the struggling service.

**No time to recover.** With zero delay, the retries arrive within milliseconds. An overloaded service often needs seconds of reduced load to drain queues, finish GC pauses, or bring new instances online. Immediate retries keep it pinned at saturation. That turns a transient blip into a sustained outage, a pattern sometimes called a *retry storm* or *metastable failure*.

**Synchronization.** Every client that saw the failure retries at the same instant, so traffic arrives in coordinated waves instead of being spread out. Even if average load is survivable, the spikes are not.

**Multiplication across layers.** If service A retries 5x into B, and B retries 5x into C, then C sees up to 36x the load (6 × 6). Retries at every layer of a call chain compound geometrically.

**Self-inflicted damage.** The calling service also suffers. Its threads and connections stay tied up waiting on doomed retries, so its latency rises, its own callers time out, and *they* retry. The failure spreads upstream.

## A better retry policy

1. **Exponential backoff.** Wait longer between attempts, for example base 100 ms doubling each time (100, 200, 400, 800 ms...), capped at a maximum such as 10–30 s.

2. **Jitter.** Randomize each delay so clients don't retry in lockstep. "Full jitter" works well: `sleep = random(0, min(cap, base * 2^attempt))`.

3. **Fewer attempts.** 2–3 retries is usually enough. Beyond that you're mostly adding load, not success.

4. **Retry only what's retryable.**
   - Retry: connection errors, timeouts, 502/503/504, and 429.
   - Don't retry: 4xx client errors like 400, 401, 403, 404, which will fail again.
   - Honor `Retry-After` headers when the server sends them.
   - Only retry idempotent operations, or use idempotency keys for non-idempotent ones like POSTs that create or charge.

5. **Retry budget.** Limit retries to a fraction of total traffic, for example retries ≤ 10% of requests over a sliding window. When most calls are failing, a budget automatically stops the amplification. A per-call max-attempts limit can't do that.

6. **Circuit breaker.** After the error rate crosses a threshold, stop calling the dependency entirely for a cooldown period and fail fast, ideally with a fallback such as cached data or degraded functionality. Then let a few probe requests through (half-open) to detect recovery.

7. **Retry at one layer only.** In a deep call chain, retry at a single layer, usually the edge or the layer closest to the failing dependency, to avoid multiplicative amplification.

8. **Deadlines.** Give the overall operation a total time budget and propagate it downstream, so you never keep retrying after the original caller has already given up.

### Example

```
max_attempts   = 3
base_delay     = 100ms
max_delay      = 10s
delay(n)       = random(0, min(max_delay, base_delay * 2^n))   # full jitter
retry_on       = {connect error, timeout, 429, 502, 503, 504}
respect        = Retry-After header
retry_budget   = 10% of requests per 10s window
circuit_breaker: open at 50% errors over 20+ requests, 30s cooldown, then half-open
```

The principle is that retries should help with *transient, isolated* failures and back off automatically during *systemic* ones. Backoff and jitter spread the load out, and budgets and circuit breakers make sure that when the dependency is truly down, you reduce pressure on it instead of adding to it.