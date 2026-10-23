## Why immediate retries made the outage worse

**1. Retries multiply load on a service that is already failing.** Each failed call is sent up to 6 times (1 try plus 5 retries). The dependency is already struggling, so it gets *more* requests exactly when it has the least capacity. Its queues grow, responses slow down, and more calls time out and trigger more retries.

**2. Retries compound across layers.** If service A retries 5 times against B, and B retries 5 times against C, one user request can produce 6 × 6 = 36 calls to C. Each extra layer multiplies the load again.

**3. Immediate retries synchronize.** When the dependency fails, many clients fail at the same moment and retry at the same moment. This creates a thundering herd that hits the dependency in spikes, just as it tries to recover.

**4. Retries delay recovery.** Once the dependency comes back, the retry backlog and the resulting connection and thread-pool exhaustion keep it overloaded.

## Retry policy I would use instead

**Retry only what is safe and likely to succeed**
- Retry transient errors: connection resets, timeouts, `429`, `502`, `503`, `504`.
- Don't retry other `4xx` responses. They will fail again.
- Only retry non-idempotent operations (like `POST`) if they carry an idempotency key.

**Keep the attempt count low**
- Use 2–3 total attempts, not 6. Most transient failures clear within one or two retries.

**Back off exponentially, with jitter and a cap**
- Wait longer after each failure, and randomize the wait so clients don't align.
- Full jitter: `sleep = random(0, min(cap, base × 2^attempt))`, with `base` around 100–500 ms and `cap` around 10–30 s.

```python
delay = random.uniform(0, min(CAP, BASE * 2 ** attempt))
time.sleep(delay)
```

**Respect server signals**
- If the response includes `Retry-After`, wait at least that long.

**Use a retry budget**
- Limit retries to a fraction of total traffic (for example, 10%) using a token bucket or similar. When the budget is exhausted, fail fast instead of retrying. This caps the amplification no matter how many clients there are.

**Add a circuit breaker**
- After the failure rate passes a threshold, stop calling the dependency for a while and fail fast.
- After a cooldown, let a few probe requests through (half-open). Close the circuit only if they succeed.

**Retry at one layer**
- Retry at the outermost layer or at a single designated layer. Inner layers should fail fast, so retries don't multiply.

**Set deadlines**
- Use a per-attempt timeout and an overall request deadline. Don't retry if the deadline has already passed.

**Monitor retry rate**
- Alert on the ratio of retries to requests. A spike in retries is an early warning of a retry storm.

In short: retry fewer times, wait longer each time with random jitter, cap total retries with a budget, stop calling a failing dependency with a circuit breaker, and retry at only one layer.