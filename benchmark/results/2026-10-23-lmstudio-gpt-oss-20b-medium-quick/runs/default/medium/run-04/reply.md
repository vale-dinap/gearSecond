**Why the “immediate‑retries‑up‑to‑5” strategy made the outage worse**

| What the code did | What actually happened in the system |
|-------------------|--------------------------------------|
| On every HTTP 5xx or timeout, the client **sent a new request right away** (no delay). | The downstream service was already down or heavily throttled. The flood of new requests hit it *again* immediately after the first failure. |
| Up to five attempts were made per call, all back‑to‑back. | Each attempt added load on the dependency – more CPU, memory, and network usage. In a cascading‑failure scenario this is called a **retry storm** or “thundering herd”. |
| The retry logic didn’t take into account the health of the downstream service. | As the downstream service struggled to keep up with the sudden surge, its response times grew, more timeouts occurred, and more retries were triggered – a vicious feedback loop that amplified the outage. |

In short: **“fire‑and‑forget” retries are a classic recipe for turning a single failure into a system‑wide spike in load and latency.**

---

## A better retry policy

The goal is to be *aggressive enough* to recover from transient glitches, but *gentle enough* not to push a failing dependency harder.

### 1. Exponential back‑off with jitter
Instead of sending the next request immediately, wait an increasing amount of time that also contains random variation (jitter). This spreads retries over time and avoids synchronised bursts.

| Retry # | Base delay (ms) | Jitter factor | Final interval (≈) |
|---------|-----------------|---------------|--------------------|
| 1       | 50              | ±20 %         | 40–60 ms           |
| 2       | 100             | ±20 %         | 80–120 ms          |
| 3       | 200             | ±20 %         | 160–240 ms         |
| 4       | 400             | ±20 %         | 320–480 ms         |
| 5       | 800             | ±20 %         | 640–960 ms         |

*The exact numbers can be tuned to the latency profile of your system.*

### 2. Total retry budget
Stop after a *maximum elapsed time*, e.g., **2 seconds** or **3 attempts** – whichever comes first. This caps the total time spent on a single operation and keeps the caller responsive.

### 3. Circuit breaker (optional but recommended)
If you observe more than, say, **30 % failures in the last minute**, open the circuit: immediately fail new calls without even trying to reach the downstream service. After a cooldown period (e.g., 10 seconds), allow a single “probe” request; if it succeeds, close the circuit.

### 4. Idempotency check
Retry only for idempotent HTTP verbs (`GET`, `HEAD`, `PUT`, `DELETE` with no side‑effects). For non‑idempotent verbs (`POST`) either avoid retries or use a safe “retry‑safe” pattern (e.g., client‑side generated idempotency keys).

### 5. Backpressure / throttling
If the service is already saturated, throttle outgoing requests: drop or queue them instead of immediately retrying. A simple token bucket can keep the rate below a chosen threshold.

---

## Putting it together – a sample policy in pseudo‑code

```python
MAX_TOTAL_TIME = 2_000            # ms
RETRY_LIMIT   = 5
BASE_DELAY    = 50                # ms
JITTER        = 0.20              # ±20%

def call_dependency():
    start_time = now()
    attempt = 0
    while True:
        try:
            return http_get(url, timeout=500)   # 500 ms request timeout
        except TransientError:                  # 5xx, network failure, etc.
            elapsed = now() - start_time
            if elapsed > MAX_TOTAL_TIME or attempt >= RETRY_LIMIT:
                raise

            delay = BASE_DELAY * (2 ** attempt)
            delay *= random.uniform(1-JITTER, 1+JITTER)

            sleep(delay)
            attempt += 1
```

*Add a circuit‑breaker wrapper around `call_dependency()` that monitors failure rate and short‑circuits the call if thresholds are exceeded.*

---

### Bottom line

- **Immediate retries** create *retry storms* that overload a failing dependency.
- Use **exponential back‑off + jitter**, a **total retry budget**, and optionally a **circuit breaker** to keep retries useful without hurting system health. This gives your service resilience while protecting its downstream partners during outages.