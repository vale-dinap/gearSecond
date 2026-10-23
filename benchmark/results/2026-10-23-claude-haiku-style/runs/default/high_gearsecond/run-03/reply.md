## Why immediate retries made the outage worse

Each failed call turned into up to 6 calls (1 original + 5 retries), all sent right away. When the dependency is already overloaded or down, that's the wrong response:

- **Load multiplies.** If every caller sends 6x its normal traffic, the struggling dependency gets more load at the moment it has the least capacity to handle it. It can't recover while the retries keep arriving.
- **Retries are synchronized.** Many callers fail at about the same time, so with no delay between attempts they all retry at about the same time. That produces repeated traffic spikes instead of a smooth load.
- **Layers compound.** If the caller's own callers also retry 5 times, the amplification is multiplicative: 6 × 6 = 36 attempts per user request, and deeper call chains are worse.
- **Retries cover up the signal.** Immediate retries often succeed or fail fast, so the caller never backs off, and the dependency's failure looks like a flood of work rather than a reason to stop.

## Retry policy I would use instead

1. **Fewer attempts.** 2 to 3 total attempts is usually enough for transient errors. More retries mostly add load without adding success.

2. **Exponential backoff with full jitter.** Wait longer after each failure and randomize the wait so callers don't move in lockstep:
   ```
   delay = random(0, min(cap, base * 2^attempt))
   ```
   For example, base = 100 ms, cap = 10 s. This spreads retries out over time instead of stacking them.

3. **Retry only what's retryable and safe.** Retry timeouts, connection resets, `429`, `502`, `503`, and `504`. Don't retry `4xx` client errors such as `400` or `401`, since they won't succeed on retry. Only retry non-idempotent operations (like POST that creates something) if you have an idempotency key.

4. **Honor `Retry-After`.** If the dependency says when to come back, use that value instead of your own schedule.

5. **Use a retry budget.** Cap retries as a fraction of total traffic (for example, retries may not exceed about 10% of requests in the last minute). When the budget is spent, fail fast. This bounds amplification no matter how many callers exist.

6. **Add a circuit breaker.** After a threshold of failures, stop calling the dependency for a cooldown period, then let a few trial requests through (half-open state). While the circuit is open, return an error or fallback immediately, which gives the dependency room to recover.

7. **Retry at one layer only.** Pick a single place (usually the outermost client or a shared library) to own retries. Other layers should pass failures up.

8. **Set an overall deadline.** Put a time limit on the whole operation, including retries, so a slow dependency can't tie up resources indefinitely.

9. **Degrade gracefully.** Where possible, serve cached data, a default, or a reduced feature set during an outage rather than retrying harder.

In short: retry a little, wait progressively longer with randomness, cap the total volume of retries, and stop calling entirely when the dependency is clearly unhealthy.