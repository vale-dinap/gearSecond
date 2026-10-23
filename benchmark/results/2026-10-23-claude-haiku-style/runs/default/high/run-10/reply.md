## Why immediate retries made the outage worse

1. **Retries multiply load on a service that is already failing.** Each failed call becomes up to 6 calls (1 original + 5 retries). If every caller does this, the dependency receives about 6x its normal traffic at the moment it has the least capacity to absorb it.

2. **The multiplication compounds across layers.** If the calling service is itself called by a service that also retries, the amplification is multiplicative. Three layers of 6 attempts each can produce 6³ = 216 calls per user request.

3. **Immediate retries give the dependency no time to recover.** Retrying in microseconds or milliseconds mostly re-sends requests that will fail for the same reason, such as a exhausted connection pool, a full queue, or a crashed instance that is restarting. The retries keep the dependency saturated instead of letting it drain its backlog.

4. **Retries synchronize.** Without randomness, every client that failed at the same moment retries at the same moment. The result is a series of traffic spikes that hit the dependency as it comes back up, which can knock it over again.

5. **Retries hold resources.** Each in-flight attempt occupies a connection, a thread, or a queue slot in both the caller and the dependency. Those resources stay occupied while the attempts time out, so new requests queue behind them.

6. **The policy is probably too broad.** Retrying 4xx responses, or non-idempotent writes without an idempotency key, can cause errors or duplicate side effects in addition to the load problem.

## Retry policy I would use instead

- **Bounded attempts.** Use 2–3 total attempts, not 6. Most transient failures clear within one or two retries, and a larger count mainly adds load.

- **Exponential backoff with full jitter.** Wait before each retry, growing the bound each time and randomizing within it:
  ```
  sleep = random(0, min(cap, base * 2^attempt))
  ```
  For example, `base = 100ms`, `cap = 10s`. Randomization spreads retries out so they stop arriving in synchronized waves.

- **Retry only transient errors.** Retry on connection resets, timeouts, `502`, `503`, `504`, and `429`. Do not retry other `4xx` responses, since they will fail again. For `429` and `503`, honor the `Retry-After` header when present.

- **Retry budget.** Cap retries at a fraction of total traffic, for example 10% over a rolling window. Once the budget is spent, fail fast. This bounds amplification no matter how many requests fail, which is the main protection against the multiplicative effect.

- **Circuit breaker.** After a threshold of consecutive failures or a high error rate, stop calling the dependency for a cooldown period. Then allow a small number of probe requests (half-open). This gives the dependency a quiet period to recover and avoids wasted calls.

- **Deadlines and timeouts.** Set an overall deadline for the whole operation, including retries, and pass the remaining time downstream. Retries should never run past the time the user is still waiting.

- **Retry at one layer only.** Retries should live in one place, typically the outermost client or the edge. Inner layers should fail fast, so amplification does not multiply across the call chain.

- **Idempotency keys for writes.** Only retry non-idempotent operations when the request carries an idempotency key that the dependency honors, so a retry cannot apply the operation twice.

- **Degrade gracefully.** When the circuit is open or the budget is spent, return a cached value, a partial response, or a clear error, and queue non-urgent work for later instead of retrying it synchronously.

- **Observability.** Track retry counts, budget exhaustion, and breaker state. These metrics show whether the policy is helping or hiding a problem.

The core change is moving from "retry fast and often" to "retry rarely, spread out, and only when the retry budget allows it," so the caller's behavior reduces load during an outage instead of adding to it.