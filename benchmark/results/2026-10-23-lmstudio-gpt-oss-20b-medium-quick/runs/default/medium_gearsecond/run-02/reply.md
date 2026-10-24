When the service retries immediately on every failure it sends a burst of duplicate requests to its dependency while that dependency is already overloaded or partially down.  
* The burst can push the downstream system over its capacity, turning a mild outage into a full‑blown one (the “thundering herd” effect).  
* Clients keep waiting for each retry to finish before finally getting an error, increasing perceived latency and user frustration.

A safer policy is **exponential backoff with jitter**:

1. Retry up to 5 times (or fewer if the operation is idempotent‑safe).  
2. Wait `delay = base * 2^attempt` milliseconds, e.g., 100 ms, 200 ms, 400 ms… up to a maximum of ~3–5 s.  
3. Add random jitter (±10–20 %) to avoid synchronized retries across many services.  

This spreads traffic, gives the downstream system time to recover, and still allows quick recovery for transient errors.