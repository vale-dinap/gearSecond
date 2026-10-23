Immediate retries make an outage worse because they multiply load on the component that is already failing.

**Why it amplifies the outage**

- **Load multiplies.** With up to 5 retries, each failed call becomes up to 6 requests. A dependency that was struggling to keep up now gets roughly 6x its normal traffic, which pushes it further past capacity.
- **Retries arrive together.** If every caller retries with no delay, their retries land in the same instant. The dependency sees a spike at each retry wave instead of a steady trickle, and it never gets a window to drain its queues and recover.
- **Retries stack across layers.** If the caller's dependencies also retry, the multiplier compounds. Three services each retrying 5 times can turn one user request into 216 calls against the bottom layer.
- **Failing requests hold resources.** Each attempt occupies connections, threads, and memory in the caller, which can exhaust the caller's own pools and take it down too.
- **Retries of non-transient errors waste capacity.** A 400 or a validation failure will never succeed on retry, so those attempts only add load.

**A better retry policy**

1. **Retry only transient failures.** Retry on timeouts, connection resets, 429, 502, 503, and 504. Don't retry other 4xx responses.
2. **Use exponential backoff with full jitter.** Wait `random(0, min(cap, base * 2^attempt))`. For example, base 100 ms and cap 10 s. The exponential growth gives the dependency recovery time, and the randomness spreads retries out so they don't synchronize.
3. **Keep the attempt count low.** Two or three attempts is usually enough. Extra attempts mostly add load after the first few have already failed.
4. **Respect `Retry-After`.** If the dependency says when to come back, wait at least that long.
5. **Use a retry budget.** Limit retries to a fraction of total traffic, such as 10%. When the budget runs out, fail fast. This caps amplification no matter how many requests fail at once.
6. **Set timeouts.** Use a per-attempt timeout and an overall deadline for the whole operation, so retries can't pile up indefinitely.
7. **Add a circuit breaker.** After a threshold of failures, stop calling the dependency for a cooldown period, then let a few trial requests through to test recovery. This turns a dependency outage into fast local failures instead of queued work.
8. **Retry at one layer only.** Let one component own retries, usually the one closest to the failing call. Other layers should fail fast.
9. **Make retried operations idempotent.** For non-idempotent calls such as POST, use idempotency keys so a retry after a timeout doesn't create duplicates.
10. **Monitor retry rates.** Track attempts per request and retry-budget usage so a rise in retries shows up before it causes an incident.

In short, the original policy retried too often, too fast, at every layer, and with no limit. The fix is to retry fewer times, wait longer between attempts with jitter, cap the total retry volume, and stop calling a dependency that is clearly down.