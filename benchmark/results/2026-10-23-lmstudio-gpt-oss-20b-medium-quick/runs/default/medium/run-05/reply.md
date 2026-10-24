**Why the “immediate‑retry‑5‑times” policy made an outage worse**

| What happened | Why it hurts a dependent service |
|---------------|----------------------------------|
| **Burst traffic** – each client call that failed was retried *right away* 5 times, so in less than a second the downstream dependency saw 6 requests instead of 1. | The dependency was already struggling (CPU/Memory exhausted, database time‑outs, network congestion).  Adding another burst of traffic pushed it over its capacity and caused more failures → more retries → a vicious cycle. |
| **No back‑off** – the retry window is effectively 0 ms between attempts. | Even if the downstream service had a small “warm‑up” period after a failure, the client never gives it any time to recover. |
| **Fixed retry count** – 5 retries regardless of error type. | Some errors are permanent (e.g., 404 Not Found, 401 Unauthorized). Retrying those just wastes resources and keeps hammering the downstream service. |
| **No jitter** – all clients retry in lock‑step when the upstream fails. | If many services are doing this at once it creates a “thundering herd” that can collapse shared resources (database connections, thread pools) on the dependent side. |

In short: *the policy created a retry storm that overloaded an already‑strained dependency and amplified the outage.*

---

## A healthier retry policy

A robust retry strategy should:

1. **Be idempotent or safe**  
   - Only retry when the operation can be repeated without side effects (e.g., GET, PUT/DELETE with idempotency keys).  
   - Skip retries for client‑side errors that are unlikely to succeed on a repeat (4xx codes other than 429/503).

2. **Use exponential back‑off + jitter**  
   ```text
   delay = base * 2^(attempt-1) + random(0, jitter)
   ```
   - `base` could be 50 ms.  
   - `jitter` up to, say, 100 ms prevents synchronized bursts.  
   - Cap the delay (e.g., max 2 s) so a request never waits too long.

3. **Limit total retry budget**  
   - Instead of “5 attempts”, consider “max total elapsed time” (e.g., 1–2 seconds).  
   - Or cap attempts to 3–4 when the downstream error is a server‑side fault (`5xx`).

4. **Short, reasonable request timeout**  
   - A retry policy only makes sense if each individual call times out fast enough that a retry isn’t just waiting for an already‑failing service.  
   - Example: 200 ms timeout per HTTP call.

5. **Circuit breaker / bulkhead**  
   - If the downstream dependency shows repeated failures, trip a circuit breaker and return a graceful error or fallback immediately.  
   - This stops the “retry storm” before it reaches the dependent system.

6. **Back‑off for specific status codes**  
   - 429 (rate limit) → exponential back‑off.  
   - 503 (service unavailable) → back‑off + circuit breaker.  

7. **Graceful degradation / fallback**  
   - If all retries fail, return a cached value or an empty result rather than propagating the error to callers.

---

### Sample pseudo‑code

```python
def call_dependency(url):
    timeout_ms = 200          # per request
    max_elapsed_ms = 1500     # total retry budget
    base_delay_ms = 50
    jitter_ms = 100
    start_time = now()

    attempt = 0
    while True:
        attempt += 1
        try:
            return http_get(url, timeout=timeout_ms)
        except TransientError as e:   # e.g., 502, 503, 504, network glitch
            elapsed = now() - start_time
            if elapsed > max_elapsed_ms or attempt >= 4:
                raise ServiceUnavailable()
            delay = base_delay_ms * (2 ** (attempt-1)) + random(0, jitter_ms)
            sleep(delay)
        except PermanentError as e:   # 404, 401, etc.
            raise
```

---

### Bottom line

The “immediate‑retry‑5‑times” policy created a *burst* of traffic that overwhelmed the dependent service during its outage.  
A healthier approach is to:

- **Retry only when safe** (idempotent ops, transient errors).  
- **Space retries out** with exponential back‑off + jitter.  
- **Cap total retry time / attempts**.  
- **Add a circuit breaker** so that repeated failures stop the storm.  

With these changes the system is more resilient: it gives the downstream dependency breathing room during an outage, and callers either succeed or fail fast without hammering the network.