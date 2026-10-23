Immediate retries turn one failure into a burst of extra load on a dependency that is already failing, so the outage lasts longer and spreads.

## Why immediate retries make the outage worse

Each caller treats a failure as “try again right now,” up to five more times. During an outage that means:

- **Load multiplies.** One user request becomes up to six calls (the original plus five retries). Every client does this at once, so traffic to the dependency can jump several times just as it is least able to handle it.
- **Recovery never starts.** The dependency stays saturated: connection pools, thread pools, and queues stay full, so requests keep timing out. Those timeouts trigger more immediate retries. The feedback loop keeps the service down after the original fault would have cleared.
- **Clients fail together.** With no delay, every caller retries in the same instant. That synchronized spike is a retry storm. It also burns the caller’s own connections and threads, so slowness in one dependency becomes failures across the service.

Retries only help when the failure is brief and rare. An outage is the opposite: widespread and ongoing. Retrying it at once spends capacity that the dependency needed in order to come back.

## Policy to use instead

Retry a small number of times, only for retryable errors, with **exponential backoff and full jitter**, and stop calling entirely when the dependency is clearly down.

1. **Retry only transient failures.** Retry connection errors, timeouts, HTTP 429, and HTTP 5xx. Do not retry most HTTP 4xx responses. Retry only operations that are safe to repeat, or send an idempotency key.
2. **Back off exponentially, then add jitter.** Wait longer after each failure, for example base 100 ms doubled each attempt, capped around 5–10 s. Sleep a random time between 0 and that delay (`sleep = random(0, min(cap, base * 2^attempt))`). The growing delay gives the dependency room to recover. The randomness keeps many clients from retrying on the same tick.
3. **Cap attempts and total time.** Three attempts is usually enough, inside a deadline shorter than the caller’s own timeout. Give up and return an error rather than spending the whole latency budget on retries.
4. **Open a circuit breaker.** After a sustained failure rate, stop sending real traffic and fail fast. Allow a few probe requests through. Close the circuit only after those succeed. This cuts the retry storm off at the source.
5. **Honor `Retry-After`.** If the dependency sends that header on HTTP 429 or 503, wait at least that long before the next attempt.

The dependency then sees a shrinking, unsynchronized trickle of retries instead of a multiplied flood, and callers fail quickly once it is clear the outage is still in progress.