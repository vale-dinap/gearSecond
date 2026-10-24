### Why Immediate Retries Made the Outage Worse

1. **Load Amplification (Retry Storm)**  
   Immediate retries flood a failing dependency with identical requests at the same rate the original traffic arrived. During an outage, the dependency is already struggling or down. Multiplying requests by 5x exacerbates queue buildup, thread/connection exhaustion, and memory pressure, turning a partial degradation into a full cascade.

2. **Wasted Client Resources**  
   Each retry consumes CPU, network sockets, and memory for doomed requests. Thread pools or connection pools in the retrying service can become exhausted, blocking legitimate requests and degrading overall system health.

3. **Delayed Detection & Recovery**  
   Immediate retries mask the true failure rate. Monitoring may not trigger alerts until downstream systems break. The dependency also gets no cooling-off period to recover, drain queues, or scale up.

4. **Thundering Herd on Recovery**  
   When the dependency finally comes back online, all 5 retries across thousands of clients fire simultaneously, causing a second wave of overload that can delay or prevent recovery.

5. **Violation of Fail-Fast Principles**  
   Retrying instantly ignores the reality of distributed systems: failures are often systemic, not transient. Blind retries delay fallbacks, circuit breaking, and graceful degradation.

---

### Recommended Retry Policy

A production-ready retry strategy should be **bounded, intelligent, and defensive**:

| Component | Recommendation | Why |
|-----------|----------------|-----|
| **Backoff** | Exponential: `base * 2^attempt` (e.g., 100ms, 200ms, 400ms, 800ms, 1.6s) | Gives the dependency time to recover; reduces load growth geometrically |
| **Jitter** | Full jitter: `random(0, min(cap, backoff))` | Prevents synchronized retries across clients (thundering herd) |
| **Retry Count** | Max 3 attempts (not 5) | Diminishing returns after 3; each retry costs more than it saves |
| **Selective Retries** | Only retry on: `5xx`, `429`, `408`, `409`, timeouts, DNS/connection errors | Do not retry `4xx` (client errors), `401/403`, or permanent failures |
| **Deadline Awareness** | Cancel retry if `elapsed_time > request_deadline * 0.7` | Avoids retrying when there's no time left to get a meaningful response |
| **Retry Budget** | Limit to e.g., 10% of total requests, or max N retries per minute per service | Prevents retry amplification from overwhelming downstream or client resources |
| **Circuit Breaker** | Open after `failure_rate > threshold` (e.g., 50% over 30s) or `consecutive_failures > 5` | Stops retries entirely during prolonged outages; fails fast instead of amplifying |

---

### Example Implementation (Conceptual)

```python
def make_request_with_retry(url, deadline):
    attempts = 0
    max_retries = 3
    base_delay_ms = 100
    cap_ms = 5000
    
    while attempts <= max_retries:
        try:
            response = http_call(url, timeout=calculate_remaining_time(deadline))
            if response.status_code < 500:
                return response
            # Retry only on server errors
        except (TimeoutError, ConnectionError, DNSException) as e:
            pass  # retry on transient network failures
        
        attempts += 1
        if attempts > max_retries:
            raise RetryExhaustedError()
        
        # Exponential backoff + full jitter
        delay = min(cap_ms, base_delay_ms * (2 ** (attempts - 1)))
        jittered_delay = random.uniform(0, delay)
        sleep(jittered_delay / 1000)
        
        # Deadline check
        if time_elapsed() > deadline * 0.7:
            raise DeadlineExceededError()
```

---

### Key Principles to Enforce

1. **Retries are a last resort, not a default behavior.** Prefer timeouts, circuit breakers, and fallbacks first.
2. **Never retry without jitter or backoff.** Immediate retries are essentially DDoS attacks on failing dependencies.
3. **Make retries idempotent.** Non-idempotent retries (e.g., POST to create orders) can cause duplicate charges, data corruption, or financial loss.
4. **Monitor retry metrics.** Track retry rate, success rate after retry, and circuit breaker state. High retry rates often indicate deeper architectural issues.
5. **Prefer `retry-after` headers.** If the dependency returns `429` or `503` with `Retry-After`, honor it.

---

### Summary
Immediate retries amplify outages by multiplying load, exhausting resources, and delaying recovery. Replace them with a **bounded exponential backoff + jitter policy**, limited to **3 attempts**, conditioned on **retryable error types**, aware of **deadlines**, and protected by a **circuit breaker**. This aligns with industry standards (AWS, Google, Netflix) and turns retries from an outage multiplier into a graceful degradation tool.