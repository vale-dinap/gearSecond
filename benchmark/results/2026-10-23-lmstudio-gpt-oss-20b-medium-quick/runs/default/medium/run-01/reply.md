### Why “5 immediate retries” made an outage **worse**

| What the policy did | Immediate effect on the client service | Impact on the downstream (dependency) | Net result |
|---------------------|----------------------------------------|---------------------------------------|------------|
| 6 calls in a row (original + 5 retries) | The caller thread is blocked for the full retry window. All 6 attempts hit the same dependency endpoint almost simultaneously. | The dependency receives *six* concurrent requests that it cannot serve because it’s already down or saturated. These extra calls consume CPU, memory, sockets, and sometimes even lock‑table rows in the downstream service. | The dependency becomes slower, returns more timeouts/failures, which feed back into the client. This creates a “retry storm” that amplifies latency and failure rate—hence the outage grows instead of shrinking. |
| No back‑off or jitter | Every retry is identical in timing (e.g., 0 ms delay). | All retries arrive at roughly the same instant, overloading the dependency’s connection pool / thread pool. | The downstream can hit hard limits (max connections, max threads) and start rejecting requests outright. |
| No circuit‑breaker | Each request always attempts to reach the dependency regardless of its recent health. | The client service keeps allocating resources for failed calls, draining its own thread pools and memory. | The client may run out of resources, causing further failures (self‑inflicted outage). |

In short: **Immediate retries create a burst of traffic that the already‑unhealthy dependency cannot absorb; this turns a single point of failure into a cascading load problem.**

---

## A better retry policy

A robust policy is built on three core ideas:

1. **Back‑off** – spread out attempts so they don’t arrive in a tight cluster.
2. **Jitter** – randomise the back‑off to avoid many services synchronising their retries.
3. **Circuit‑breaker / timeout guard** – stop retrying once failure rates look unhealthy.

Below is a typical pattern you can adopt (pseudo‑code, but it maps directly onto libraries such as Polly, Resilience4j, Spring Retry, etc.):

```text
maxAttempts      = 5
initialDelayMs   = 100        // first back‑off delay
multiplier       = 2          // exponential factor
maxDelayMs       = 2000       // cap the maximum wait
jitterFraction   = 0.1        // ±10% random jitter

for attempt in 1..maxAttempts:
    try:
        response = callDependency()
        if isSuccessful(response):
            return response          // success – stop retrying
    except (Timeout, ServiceUnavailable) as e:
        # Record the failure in a circuit‑breaker window
        recordFailure()

    # If we’re here, it failed – decide whether to continue
    if circuitBreakerOpen():
        raise ServiceException("Dependency unavailable")   // give up early

    # Compute exponential back‑off with jitter
    delay = min(initialDelayMs * (multiplier ** (attempt - 1)), maxDelayMs)
    jitter = randomUniform(-jitterFraction, +jitterFraction) * delay
    sleep(delay + jitter)

# All attempts failed – surface the error to caller
raise ServiceException("All retries exhausted")
```

### Key points of this policy

| Feature | Why it matters |
|---------|----------------|
| **Exponential back‑off** (100 ms → 200 ms → 400 ms …) | Gives the downstream time to recover; avoids hammering a down service. |
| **Jitter** (±10 %) | Prevents many services from retrying at exactly the same moments, which would create new “retry storms.” |
| **Maximum delay cap** (2 s in example) | Keeps total latency bounded while still giving some breathing room to the dependency. |
| **Circuit‑breaker guard** | After a short window of consecutive failures (e.g., 3/5), stop retrying and fail fast, freeing resources for other work. |
| **Idempotency check** | Only retry if the operation is safe to repeat (GET, idempotent POST, etc.). For non‑idempotent writes, either use a fallback or avoid retries altogether. |

### How this mitigates outages

1. **Load spreading** – The dependency sees at most one request every ~100 ms per client service instance instead of 6 simultaneous calls.
2. **Graceful degradation** – If the circuit‑breaker trips, the client immediately returns an error (or a cached/fallback response) without tying up threads.
3. **Reduced risk of cascading failures** – Each downstream component can handle its own back‑off; no single service floods another.
4. **Observability** – The retry loop can expose metrics (retry count, delay distribution, circuit‑breaker state) that help operators see when a dependency is under stress.

---

## Practical implementation tips

| Tool / Framework | How to configure |
|------------------|-----------------|
| **Polly (C#)**  | `Policy.Handle<Exception>().WaitAndRetryAsync(retryCount, retryAttempt => TimeSpan.FromMilliseconds(100 * Math.Pow(2, retryAttempt - 1)) + jitter)`. Add a circuit breaker with `CircuitBreakerAsync` or use the `BulkheadPolicy` to limit concurrent calls. |
| **Resilience4j (Java)** | `RetryConfig.custom().maxAttempts(5).waitDuration(Duration.ofMillis(100)).exponentialBackoffFactor(2).build();` plus `CircuitBreakerConfig`. |
| **Spring Retry** | Use `@Retryable(value = {HttpServerErrorException.class}, maxAttempts=5, backOffPeriod=100, multiplier=2)` and add a fallback method. |
| **Go (golang)** | Wrap the HTTP client call in a loop with `time.Sleep` using exponential back‑off and random jitter (`rand.Float64()`). Use a context with deadline to enforce overall timeout. |

---

## Bottom line

Immediate retries are a *dangerous* pattern when a dependency can be down. They create a “retry storm” that overloads the downstream service, inflates latency for all callers, and can trigger cascading failures.

A safer policy uses **exponential back‑off with jitter** plus a **circuit‑breaker** (and optional fallback). This spreads traffic, protects both sides of the call chain, and keeps outages from blowing out into larger system problems.