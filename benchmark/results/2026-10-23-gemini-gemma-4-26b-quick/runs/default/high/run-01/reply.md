This phenomenon is known as a **Retry Storm** (or **Retry Amplification**). Instead of helping the system recover, the retry logic acts as a self-inflicted Distributed Denial of Service (DDoS) attack against the already struggling dependency.

### Why the outage got worse

The failure occurred due to three main factors:

1.  **Traffic Amplification:** If a service receives 1,000 requests per second and the dependency fails, the immediate retry policy turns those 1,000 requests into 5,000 additional requests (6,000 total including the original). This exponentially increases the load on a dependency that is likely already struggling with resource exhaustion (CPU, memory, or connection pools).
2.  **Lack of "Breathing Room":** By retrying **immediately**, the service provides zero time for the dependency to clear its internal queues, perform garbage collection, or recover from a transient spike. It essentially hammers the dependency at the exact moment it is most vulnerable.
3.  **The "Thundering Herd" Problem:** Because the retries are immediate and likely triggered by the same error condition, all instances of the calling service will retry at the exact same millisecond. This creates massive, synchronized spikes of traffic that prevent the dependency from ever stabilizing.

---

### The Recommended Retry Policy

To prevent this, you should implement a multi-layered approach consisting of **Exponential Backoff**, **Jitter**, and a **Circuit Breaker**.

#### 1. Exponential Backoff
Instead of retrying immediately, you increase the wait time between each successive retry. This spreads the load over time and gives the dependency a chance to recover.
*   **Example:** Wait 100ms, then 200ms, then 400ms, then 800ms.
*   **Formula:** $delay = base\_delay \times 2^{attempt}$

#### 2. Jitter (Randomization)
Exponential backoff alone is not enough because multiple service instances might still sync up their retry cycles (e.g., they all wait exactly 200ms and then all hit the dependency at once). **Jitter** adds a random variable to the delay to break this synchronization.
*   **Full Jitter Formula:** $sleep = random(0, base\_delay \times 2^{attempt})$
*   This ensures that the retries are distributed smoothly across the timeline rather than arriving in "clumps."

#### 3. The Circuit Breaker Pattern
Retries should only be used for **transient** errors (like a momentary network blip). If the dependency is experiencing a hard outage, retrying is futile and wasteful. 
A Circuit Breaker monitors the failure rate:
*   **Closed State:** Normal operation; requests flow through.
*   **Open State:** If the failure rate exceeds a threshold (e.g., 50% failure over 30 seconds), the circuit "trips." The service **stops trying to call the dependency entirely** and immediately returns an error to the caller. This gives the dependency total isolation to recover.
*   **Half-Open State:** After a "sleep window," the circuit allows a small amount of test traffic through. If these succeed, the circuit closes; if they fail, it opens again.

#### 4. Retry Budgets (Optional but Advanced)
To prevent retries from consuming too much of your total bandwidth, implement a **Retry Budget**. For example, you might dictate that retries can only account for a maximum of 10% of the total request volume. If the ratio of retries to original requests exceeds 10%, the service stops retrying and only sends original requests.

### Summary Comparison

| Feature | Bad Policy (Current) | Good Policy (Proposed) |
| :--- | :--- | :--- |
| **Timing** | Immediate | Exponential Backoff |
| **Synchronization** | High (Thundering Herd) | Low (Jitter/Randomness) |
| **System Protection** | None (Amplifies Load) | Circuit Breaker (Stops Load) |
| **Goal** | Success at all costs | System stability and recovery |