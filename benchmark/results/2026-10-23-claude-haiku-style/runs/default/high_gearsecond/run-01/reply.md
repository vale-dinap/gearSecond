## Why immediate retries made the outage worse

- **Load multiplies.** Each failed call becomes up to 6 requests (1 + 5 retries). The dependency is already struggling, so it receives several times its normal load at the moment it has the least capacity.
- **Retries arrive together.** With no delay, every caller that failed at the same moment retries at the same moment. The dependency gets synchronized spikes instead of a steady trickle, so it can't recover between bursts.
- **Retries don't give the dependency time.** Recovery often needs seconds to minutes of reduced load. Five instant retries finish within milliseconds, so they add pressure without any chance for the system to heal.
- **Retries hold resources.** Threads, connections, and queue slots stay occupied while retrying, so the calling service slows down and can fail on its own.
- **Layers compound.** If several services in the call chain each retry 5 times, the amplification is multiplicative: 6 × 6 × 6 = 216 requests for one original call.

## Retry policy I would use instead

1. **Exponential backoff with full jitter.** Wait `random(0, min(cap, base × 2^attempt))`. For example, base 200 ms, cap 10 s. The jitter spreads retries out so they don't synchronize.
2. **Few attempts.** Use 2 to 3 total attempts. Beyond that, extra retries rarely succeed and mostly add load.
3. **Retry only transient failures.** Retry on connection resets, timeouts, 429, 502, 503, and 504. Don't retry 400, 401, 403, or 404, since they will fail the same way again.
4. **Honor `Retry-After`.** If the dependency sends it, wait at least that long.
5. **Retry budget.** Cap retries at a fraction of total traffic, for example 10%. When the budget is exhausted, fail fast. This bounds amplification no matter how many calls are failing.
6. **Circuit breaker.** After a threshold of failures, stop calling the dependency for a cooldown period, then let a few probe requests through. This protects the dependency while it is down and avoids wasting time on calls that will fail.
7. **Timeouts and an overall deadline.** Set a per-attempt timeout and a total deadline for the whole operation, so retries can't stall the caller indefinitely.
8. **Retry at one layer only.** Pick a single layer (usually the client library or the outermost caller) to own retries. Other layers should fail fast.
9. **Idempotency for writes.** Only retry non-idempotent operations such as POST when they carry an idempotency key, so a retry can't create duplicates.
10. **Monitor retries.** Track retry rate, budget usage, and circuit state. A rising retry rate is an early warning of a dependency problem.