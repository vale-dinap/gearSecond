Immediate retries cause the client to hammer the downstream service with many rapid requests.  
During an outage that dependency is already overloaded or unresponsive; each retry adds extra traffic, amplifying the failure and prolonging the outage for everyone.

A better policy uses *exponential back‑off with jitter*:

1. **Retry limit** – keep a small cap (e.g., 5 attempts) to avoid endless loops.  
2. **Back‑off interval** – double the wait each time: 100 ms, 200 ms, 400 ms, … up to a maximum (e.g., 3 s).  
3. **Jitter** – add random variation (±25 %) so retries from many clients don’t synchronize and spike traffic.  
4. **Circuit breaker** – after a configurable number of failures open the circuit for a set period, preventing further requests until health is restored.

This approach spreads retry traffic over time, gives the downstream service breathing room, and protects both systems during outages.