This phenomenon is known as a **Retry Storm** (or a "Thundering Herd" problem). By retrying immediately and aggressively, the service inadvertently performs a **self-inflicted Distributed Denial of Service (DDoS) attack** on its own dependency.

### Why the outage was made worse

When a dependency fails or slows down, the following chain reaction occurs:

1.  **Traffic Amplification:** If the service is configured to retry 5 times, every single failed request is transformed into 6 total requests (1 original + 5 retries). If the service handles 1,000 requests per second, a dependency failure suddenly spikes the load to 6,000 requests per second.
2.  **Elimination of Recovery Time:** Dependencies often fail because they are overloaded or struggling with resource exhaustion (CPU, memory, or database connections). By retrying *immediately*, the service does not give the dependency any "breathing room" to clear its queues, finish garbage collection, or restart.
3.  **Synchronization (The "Pulse" Effect):** Because the retries happen "immediately," many instances of your service will likely fail at the same time and retry at the exact same time. This creates massive, synchronized spikes of traffic that hammer the dependency in rhythmic waves, making it impossible for the dependency to stabilize.
4.  **Cascading Failure:** The increased load on the dependency causes it to respond even more slowly, which causes more timeouts in your service, which triggers even more retries. This creates a feedback loop that can crash not just the dependency, but also the calling service due to thread/connection exhaustion.

---

### The Recommended Retry Policy

To prevent this, you should implement a strategy based on three core components: **Exponential Backoff**, **Jitter**, and a **Circuit Breaker**.

#### 1. Exponential Backoff
Instead of retrying immediately, you increase the wait time between each successive attempt. This spreads the load over a longer period.
*   *Attempt 1:* Wait 100ms
*   *Attempt 2:* Wait 200ms
*   *Attempt 3:* Wait 400ms
*   *Attempt 4:* Wait 800ms
*   *Attempt 5:* Wait 1600ms

#### 2. Jitter (Randomization)
This is the most critical addition. Even with exponential backoff, if 100 instances fail at the same time, they will all retry at the exact same intervals (100ms, then 200ms, etc.). 

**Jitter** adds a random variable to the delay. Instead of waiting exactly 200ms, an instance might wait 187ms, while another waits 212ms. This breaks the synchronization of the "thundering herd" and smoothes out the traffic spikes into a steady, manageable flow.

> **Formula:** `delay = (base * 2^attempt) + random_jitter`

#### 3. The Circuit Breaker Pattern
While retries handle *transient* errors (a single dropped packet), they are the wrong tool for *persistent* outages. You should wrap your calls in a **Circuit Breaker**.

The Circuit Breaker tracks the success/failure rate:
*   **Closed State:** Requests flow normally.
*   **Open State:** If the failure rate hits a certain threshold (e.g., 50% failure over 30 seconds), the circuit "trips." The service **stops attempting any calls** to the dependency for a set "sleep window" (e.g., 30 seconds). It returns an immediate error to the user without even hitting the network.
*   **Half-Open State:** After the sleep window, the service allows a small amount of "test" traffic through. If those succeed, the circuit closes; if they fail, the circuit opens again.

### Summary Table

| Feature | Bad Policy (Immediate) | Good Policy (Resilient) |
| :--- | :--- | :--- |
| **Timing** | Constant/Immediate | Exponentially increasing |
| **Traffic Pattern** | Spiky/Synchronized | Smooth/Randomized |
| **Load on Dependency** | Multiplies the stress | Reduces the stress |
| **Failure Handling** | Keeps hitting a broken wall | "Circuit Breaker" stops hitting the wall |