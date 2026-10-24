### Why it made the outage worse

The service created a **retry storm** (or "thundering herd" effect). When the dependency slowed down or failed, the service immediately sent up to five additional requests for every single failed call. 

This caused several compounding issues:
1.  **Amplified Traffic:** A small increase in failed requests turned into a massive spike in total request volume, potentially multiplying the load by 5x or 6x.
2.  **Resource Exhaustion:** The dependency, already struggling, was bombarded with a surge of new connections and processing requests, preventing it from recovering.
3.  **Congestion Collapse:** The increased load likely filled up connection pools, buffers, and CPU cycles on both the service and the dependency, turning a minor hiccup into a total system failure.

---

### Recommended Retry Policy

To prevent this, you should implement a strategy that spreads out the load and gives the dependency "breathing room" to recover.

#### 1. Exponential Backoff
Instead of retrying immediately, increase the wait time between each attempt (e.g., 100ms, 200ms, 400ms, 800ms). This ensures that as failures persist, the pressure on the dependency decreases.

#### 2. Jitter (Randomness)
Even with exponential backoff, many clients might retry at the exact same synchronized intervals, creating new spikes of traffic. Adding **jitter** (randomizing the delay slightly) breaks this synchronization and spreads the load evenly over time.

#### 3. Circuit Breaker Pattern
If the failure rate exceeds a certain threshold, the "circuit" should trip and open. While the circuit is open, the service **stops attempting to call the dependency altogether** for a set period, returning an immediate error to the caller. This provides the dependency with a complete period of rest to recover its resources.

#### Summary of a robust policy:
*   **Retry Limit:** Keep a reasonable maximum (e.g., 3–5).
*   **Delay:** Exponential backoff + Jitter.
*   **Safety Valve:** Circuit breaker to halt traffic during sustained outages.