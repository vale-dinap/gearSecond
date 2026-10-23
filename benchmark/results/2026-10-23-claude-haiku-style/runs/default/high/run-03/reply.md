## Why immediate retries made the outage worse

**Retries add load exactly when the dependency can least handle it.** If the dependency is failing because it's overloaded, every failed call the service retries is extra traffic sent to a system that's already struggling.

**Five retries multiply the load.** Each logical request becomes up to 6 attempts. If the calling service gets 1,000 requests per second during the outage, the dependency sees up to 6,000 per second. If other services retry the same way, the multiplication compounds across layers: 6 × 6 = 36 attempts per user action if two layers both retry.

**Immediate retries don't give the dependency time to recover.** Retrying within milliseconds mostly hits the same overload condition again, so most retries also fail.

**Retries are synchronized.** Many clients failing at the same moment retry at the same moment, producing bursts that keep the dependency saturated instead of letting its queue drain.

**Retries tie up the caller's resources.** Threads, connections, and memory are held while retries run. The caller's own latency rises, its queues fill, and it starts timing out, which can trigger still more retries. This feedback loop is a retry storm, a form of metastable failure where the system stays broken even after the original trigger is gone.

## A better retry policy

1. **Retry only transient failures.** Retry connection resets, timeouts, and 502/503/504. Honor 429 and its `Retry-After` header. Don't retry other 4xx errors, since they will fail again. Treat generic 500s cautiously.

2. **Make retries safe.** Only retry idempotent operations, or send an idempotency key with non-idempotent requests like POST so the dependency can deduplicate.

3. **Use exponential backoff with full jitter.** Wait `random(0, min(cap, base × 2^attempt))`. For example, base 200 ms, cap 10–20 s. Jitter spreads retries out so clients don't all retry together.

4. **Cap the attempts.** Two or three total attempts is often enough. Five immediate retries is rarely justified.

5. **Use a retry budget.** Allow retries only up to a fraction of normal traffic, such as 10% of requests over a sliding window. This bounds amplification no matter how many requests fail, and it's the most effective protection against storms.

6. **Add a circuit breaker.** After a threshold of failures, stop calling the dependency for a cool-down period and fail fast. Then let a small number of probe requests through (half-open). This stops retries entirely while the dependency recovers.

7. **Respect the overall deadline.** Propagate a request deadline and don't start a retry that can't finish within it.

8. **Retry at one layer only.** If the edge, the service, and the client all retry, the amplification multiplies. Choose one layer to own retries and have the others fail fast.

9. **Watch the metrics.** Track retry rate, attempts per request, and breaker state. A rising retry ratio is an early warning of a storm.

Here is a sketch of the core logic:

```python
def call_with_retries(fn, max_attempts=3, base=0.2, cap=10.0):
    for attempt in range(max_attempts):
        try:
            return fn()
        except TransientError as err:
            if attempt == max_attempts - 1:
                raise
            if not budget.try_acquire():   # retry budget / breaker check
                raise
            time.sleep(random.uniform(0, min(cap, base * 2 ** attempt)))
```

The main idea is that retries should be rare, spread out, bounded, and stopped entirely when the dependency is clearly down. The circuit breaker and retry budget matter more than the exact backoff numbers.