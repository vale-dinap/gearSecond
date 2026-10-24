### Why immediate retries worsen outages

When a dependency fails due to overload, immediate retries create a **retry storm**. Instead of allowing the dependency to recover, the service sends a massive surge of additional traffic (the original requests plus the retries). This constant pressure prevents the dependency from clearing its queue or stabilizing, effectively turning a temporary slowdown into a total collapse.

### Recommended Retry Policy

To prevent this, you should implement a policy combining **Exponential Backoff** and **Jitter**:

1.  **Exponential Backoff:** Instead of retrying immediately, increase the wait time between each attempt (e.g., 1s, 2s, 4s, 8s...). This gives the dependency breathing room to recover.
2.  **Jitter (Randomization):** Add a random delay to the backoff intervals. If many clients retry at the exact same exponentially increasing intervals, they will still hit the dependency in synchronized waves. Jitter breaks these waves, spreading the load evenly over time.
3.  **Circuit Breaker:** Supplement retries with a circuit breaker pattern. If the failure rate exceeds a specific threshold, the breaker "trips," and the service stops attempting all calls to that dependency for a set period. This provides an immediate "cool-down" period for the failing system.