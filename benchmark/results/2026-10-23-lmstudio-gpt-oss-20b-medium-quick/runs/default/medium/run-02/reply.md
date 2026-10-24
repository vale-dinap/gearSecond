**Why the “immediate‑retry‑5‑times” strategy made an outage worse**

| Problem | What happened in the real world | Why it hurts |
|---------|---------------------------------|--------------|
| **Burst of traffic to a failing service** | Each call that failed was retried *right away* (0 ms delay) up to 5 times. | The dependency saw 5× the load from a single request, often while it was already in an error state or throttled. That extra traffic can push it over its capacity limits and trigger more failures—creating a *retry storm*. |
| **Increased latency for callers** | Every retry adds ~1–2 ms of overhead (network round‑trip, serialization, etc.). With 5 retries the caller’s request time multiplied by 5. | In a cascade outage, the original failure is already slow; adding more delays can push downstream services over their own timeout thresholds and cause cascading failures. |
| **Resource exhaustion on the client** | The client keeps the request object, open sockets, timers, etc., for each retry until all attempts finish or time out. | If many requests are retried in parallel (as often happens when a service goes down), memory, thread‑pool, and socket resources can be exhausted on the calling side, leading to slow‑down or crash of the client itself. |
| **Thundering herd / “snowball” effect** | When the downstream dependency recovers, all cached retry timers fire at once (because they were scheduled immediately). | A sudden surge in traffic overwhelms the recovering service again, prolonging the outage. |

In short: *immediate retries amplify the load on an already‑strained system and can create a vicious cycle of overload → failure → more overload*.

---

## A better retry policy

A robust policy usually combines **exponential back‑off + jitter**, **circuit breaking**, and **operation‑specific rules**. Below is a practical template you could adopt:

| Component | What it does | Typical parameters |
|-----------|--------------|--------------------|
| **Initial delay** | First wait before retrying (to give the dependency a chance to recover). | 100 ms – 200 ms |
| **Back‑off multiplier** | Each subsequent delay is multiplied by this factor. | 2× (doubling) |
| **Maximum delay** | Caps the back‑off to avoid very long waits that waste resources. | 1 s – 5 s (depending on SLA) |
| **Jitter** | Randomizes each delay within a small window to break up synchronized retries. | ±25 % of the calculated delay |
| **Maximum attempts** | Total number of tries (including the original). | 3–4 for idempotent reads, 1 for non‑idempotent writes |
| **Circuit breaker** | Stops sending requests when failure rate exceeds a threshold; opens circuit for a cooldown period. | Failure threshold: 30 % in last 60 s; open duration: 30 s – 2 min |

### Example algorithm (pseudo‑code)

```python
def call_with_retry(request, max_attempts=4):
    delay = 0.15      # 150 ms initial delay
    for attempt in range(1, max_attempts + 1):
        try:
            return send_request(request)
        except TransientError as e:
            if attempt == max_attempts or circuit_breaker.is_open():
                raise   # give up

            # exponential back‑off with jitter
            jitter = random.uniform(-0.25, 0.25) * delay
            sleep_time = min(delay + jitter, MAX_DELAY)
            time.sleep(sleep_time)

            delay *= BACKOFF_MULTIPLIER
```

### Why this works

1. **Reduces load spikes** – By spacing retries out, each retry arrives when the downstream system is more likely to be healthy.
2. **Limits total latency** – Exponential back‑off keeps the overall wait time bounded (e.g., 150 ms + 300 ms + 600 ms ≈ 1 s for three attempts).
3. **Avoids thundering herd** – Jitter ensures retries from many callers are spread over time.
4. **Prevents cascading failures** – Circuit breaker stops traffic when the dependency is clearly down, allowing it to recover before we start sending more requests.
5. **Handles different operation types** – For non‑idempotent writes you might set `max_attempts = 1` or a single retry with a very short delay; for reads you can afford more attempts.

---

### Quick checklist for your team

- [ ] Add exponential back‑off + jitter to all external HTTP calls.
- [ ] Implement a circuit breaker that opens after **X** consecutive failures or a failure rate > Y%.
- [ ] Tune `max_attempts` per endpoint (reads vs writes).
- [ ] Set an overall timeout per request (e.g., 2–3 s) to avoid hanging callers.
- [ ] Log retry attempts and failures so you can see when the policy kicks in.

By moving from “retry immediately, five times” to a disciplined back‑off strategy with circuit breaking, you’ll make your service resilient during dependency outages instead of amplifying them.