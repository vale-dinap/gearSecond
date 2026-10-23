## Why immediate retries made the outage worse

- **Load multiplies.** Each failed call becomes up to 6 attempts (1 original + 5 retries). If the dependency is already failing, its load goes up roughly 6x at the moment it has the least capacity.
- **No time to recover.** Retrying immediately gives the dependency no pause to clear its queues, restart, or drain connections. Each retry arrives while the problem still exists.
- **Synchronized clients.** Many callers fail at the same moment and retry at the same moment, so the dependency gets bursts of traffic rather than a smooth load.
- **Timeouts hold resources.** Slow or hung calls keep threads, sockets, and connections busy in the caller, which can exhaust the caller's own resources too.
- **Retries stack across layers.** If the caller's callers also retry, the effective multiplier is the product of every layer's attempts, so 5 retries at three layers can mean 216 attempts for one user request.

## Retry policy I would use instead

1. **Retry only what is safe and likely to succeed.**
   - Retry: connection resets, timeouts before a response, `429`, `503`, and `502`/`504` from a gateway.
   - Don't retry: `4xx` client errors other than `429`, and non-idempotent requests (such as `POST` that creates a charge) unless they carry an idempotency key.

2. **Use exponential backoff with full jitter and a cap.**
   ```
   delay = random(0, min(cap, base * 2^attempt))
   ```
   For example, `base = 200 ms`, `cap = 10 s`. Jitter spreads retries out so clients don't come back in lockstep.

3. **Keep the attempt count low.** Two or three attempts total is usually enough. More attempts mostly add load without improving success.

4. **Honor server signals.** If the response includes `Retry-After`, wait at least that long. Treat it as a hint to back off, not a suggestion to ignore.

5. **Set a retry budget.** Allow retries only while they are a small fraction of total traffic, for example 10%. When the budget is exhausted, fail fast. This caps amplification during an outage regardless of how many requests are failing.

6. **Add a circuit breaker.** After a threshold of consecutive failures, stop calling the dependency for a cooldown period. Let a few probe requests through to detect recovery, then close the circuit gradually.

7. **Bound the whole operation with a deadline.** Give each attempt its own timeout and the overall request a total deadline. Don't start a retry that cannot finish before the deadline.

8. **Retry at one layer only.** Pick one place in the call chain to own retries, usually the outermost caller that can make a sensible decision, and make inner layers fail fast. This keeps the multiplier at 1 instead of letting it compound.

9. **Observe it.** Track retry counts, budget exhaustion, and circuit state. Alert on sudden rises in retries, since they often show a problem before error rates do.

With this policy, a dependency outage produces a bounded, decreasing load from the caller, which gives the dependency room to recover instead of pushing it further down.