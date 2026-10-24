During an outage the downstream service is already overloaded or down.  
Immediate, back‑to‑back retries add extra traffic on top of the existing load.  
Each retry consumes CPU, memory and network bandwidth in both services, so the
system quickly becomes saturated. The added latency from repeated attempts can
also cause timeouts that cascade further failures (e.g., downstream queues fill,
other clients time out). Thus the outage is amplified rather than mitigated.

A better policy:

* **Retry limit** – keep a small cap (e.g., 3–5 attempts) but don’t retry instantly.
* **Exponential back‑off** – double the wait each attempt: 100 ms, 200 ms,
400 ms… up to a maximum delay (≈2–4 s).
* **Jitter** – add random variation (±10–20 %) to avoid thundering herd.
* **Circuit breaker** – after a threshold of consecutive failures open the
circuit for a period, then allow a few “probe” requests.

This reduces traffic spikes during outages, gives the failing service time to recover,
and prevents cascading failure.