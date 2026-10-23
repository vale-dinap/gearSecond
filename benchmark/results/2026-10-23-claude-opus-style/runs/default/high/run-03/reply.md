## Why immediate retries made the outage worse

**1. Load amplification.** Each failing request becomes up to 6 requests (1 original + 5 retries). When the dependency is already struggling, its inbound traffic suddenly multiplies by as much as 6×, exactly when it has the least capacity. If there are multiple layers that each retry (A → B → C, each with 5 retries), the multiplication compounds: 6 × 6 = 36× at the bottom.

**2. No recovery window.** Retrying *immediately* gives the dependency no time to shed load, restart, drain queues, or let autoscaling catch up. Every time it frees capacity, the retry flood consumes it again. This is how a brief blip turns into a sustained outage, sometimes called a **retry storm**.

**3. Synchronization.** When the dependency fails, every client sees the failure at about the same moment and retries at about the same moment. These synchronized waves hit the recovering service in spikes, a "thundering herd," instead of a smooth load it might be able to handle.

**4. Retrying the unretryable.** If the policy retries on every failure, it also retries errors that will never succeed (400s, auth failures) or that explicitly mean "back off" (429, 503 with `Retry-After`). That is wasted load at best, and it ignores the server's own request to slow down.

**5. Self-inflicted resource exhaustion.** The calling service holds threads, connections, and memory while it loops through retries. Latency grows, its own callers time out, and *they* retry. The failure spreads upstream.

## A better retry policy

**Exponential backoff with jitter.** Space out the attempts and randomize the delays:

```
delay = random(0, min(cap, base * 2^attempt))   # "full jitter"
```

For example, base = 100 ms and cap = 10–20 s. The backoff gives the dependency room to recover, and the jitter breaks up synchronized waves.

**Fewer attempts.** Make 2–3 retries, not 5. Most transient failures clear on the first retry. Beyond that you are mostly adding load.

**Retry only retryable failures.**
- Retry on connection errors, timeouts, 502/503/504, and 429.
- Never retry other 4xx errors.
- Honor `Retry-After` headers.
- Only retry non-idempotent operations (POST, payments, etc.) if you use idempotency keys.

**A retry budget.** Cap retries as a fraction of total traffic, for example at most 10% extra requests per client, using a token bucket. When many calls fail, retries are automatically throttled. This bounds amplification to about 1.1× instead of 6×.

**A circuit breaker.** After the failure rate crosses a threshold, stop calling the dependency for a cooldown period and fail fast or serve a fallback. Then let a few probe requests through (half-open) before resuming fully. This is what really protects a dependency that is down, as opposed to one that is flaky.

**Retry at one layer only.** In a call chain, let a single layer (usually the edge or the caller closest to the user) own retries. Inner layers fail fast. This prevents multiplicative amplification.

**An overall deadline.** Bound the total time, including all retries, by the caller's deadline, and propagate deadlines downstream. Never retry if the result will arrive after the caller has given up.

### Summary

> Up to 3 attempts total, exponential backoff with full jitter (100 ms base, ~10 s cap), only on transient errors and idempotent requests, honoring `Retry-After`, constrained by a ~10% retry budget, behind a circuit breaker, within an overall request deadline.

The general principle: retries are a tool for handling **transient, isolated** failures. During a **systemic** failure they must back off or shut off, or they become a load generator aimed at the component least able to absorb it.