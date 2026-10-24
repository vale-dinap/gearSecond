**Why the aggressive “retry‑up‑to‑5‑times‑immediately” policy made an outage worse**

| What the code did | Why it hurt the dependent service during an outage |
|-------------------|----------------------------------------------------|
| **Zero wait between retries** – the client sent 5 new HTTP requests in a tight burst as soon as the first one failed. | *Back‑pressure* on the dependency. Even if the downstream system was already overloaded or partially down, it still had to accept and process each retry request. The extra traffic increased CPU/memory usage, widened response times, and in many cases caused more timeouts or 5xx errors. |
| **No jitter** – every client hit the same endpoint at the same instant. | *Thundering‑herd* effect. When dozens/hundreds of services all retry immediately, they amplify the load spike into a “retry storm”. The dependency can quickly exhaust its resources and start rejecting requests, which in turn triggers more retries from other clients—a vicious cycle that spreads the failure. |
| **Retry on every error** – including client‑side errors (4xx) or non‑idempotent calls. | Unnecessary traffic and side‑effects. A 404 or 400 is a permanent failure; retrying it only wastes bandwidth and adds load. Non‑idempotent retries can cause duplicate writes, which may trigger further failures downstream. |
| **Blocking threads while waiting for the next retry** | Reduced concurrency of the calling service itself. Threads were tied up in the retry loop, limiting how many new requests could be processed, thereby throttling the whole system. |

In short, the policy turned a *transient* problem (the dependency was just momentarily slow or timing‑out) into a *system‑wide* congestion problem.

---

## A better retry strategy

A resilient retry policy should:

1. **Only retry on truly transient conditions**  
   - Network failures (socket timeouts, DNS lookup errors, connection reset).  
   - 5xx server errors that are likely to succeed after a short delay.  
   - Avoid retrying 4xx errors and non‑idempotent operations unless you can guarantee safe re‑execution.

2. **Use exponential back‑off with jitter**  
   ```text
   attempt 1: wait 100 ms ± random(0–50 ms)
   attempt 2: wait 200 ms ± random(0–100 ms)
   attempt 3: wait 400 ms ± random(0–200 ms)
   (max delay capped at, say, 2 s)
   ```
   *Why*: Back‑off gives the dependency a chance to recover; jitter spreads retries across time so that many clients don’t hit the service simultaneously.

3. **Cap total retry attempts and cumulative wait**  
   - Max 3–4 attempts is usually enough; more retries add diminishing returns while still adding load.  
   - If the total elapsed time (original call + all back‑offs) exceeds a threshold (e.g., 5 s), give up and surface an error to the caller.

4. **Implement a circuit breaker**  
   - After `N` consecutive failures in a short window, *open* the circuit for a cooldown period (e.g., 30–60 s).  
   - While open, return a cached fallback or a “service unavailable” response immediately instead of attempting to contact the downstream service.  
   - Periodically allow one “test” request; if it succeeds, close the circuit.

5. **Use timeouts wisely**  
   - Set a generous but bounded timeout on each HTTP call (e.g., 2 s).  
   - Combine this with the back‑off: a failure is only retried if the call timed out or received a transient error; hard failures (4xx) are not retried.

6. **Monitor and adjust**  
   - Collect metrics: retry counts, success/failure rates, latency distributions, circuit‑breaker state changes.  
   - Tune `max_attempts`, `base_delay`, `jitter_range`, and circuit‑breaker thresholds based on real traffic patterns.

---

### Example (pseudo‑code)

```python
MAX_ATTEMPTS = 4
BASE_DELAY_MS = 100
MAX_JITTER_MS = 200
CIRCUIT_BREAKER_THRESHOLD = 5
CIRCUIT_OPEN_TIME_SEC = 30

def call_dependency():
    if circuit_breaker.is_open():
        raise ServiceUnavailableError("Circuit open – dependency unavailable")

    attempt = 0
    while attempt < MAX_ATTEMPTS:
        try:
            response = http_client.get(url, timeout=2.0)
            # Treat 5xx as transient; others as final.
            if response.status_code >= 500:
                raise TransientError()
            return response
        except (TransientError, socket.timeout) as e:
            attempt += 1
            if attempt == MAX_ATTEMPTS:
                circuit_breaker.record_failure()
                raise e
            delay = BASE_DELAY_MS * (2 ** (attempt - 1))
            jitter = random.randint(0, MAX_JITTER_MS)
            time.sleep((delay + jitter) / 1000.0)

    # If we get here, all attempts failed
    raise ServiceUnavailableError("All retries exhausted")
```

*Key points in the code:*  
- **Circuit breaker** protects against retry storms.  
- **Exponential back‑off + jitter** smooths traffic.  
- **Limited attempts** keep total latency bounded.

---

## Bottom line

An “immediate, five‑times” retry policy is a classic recipe for turning an isolated failure into a cascading outage. By constraining retries to *transient* errors, adding *exponential back‑off with jitter*, capping the number of attempts, and guarding with a circuit breaker, you give both the caller and the callee room to recover while keeping overall system stability intact.