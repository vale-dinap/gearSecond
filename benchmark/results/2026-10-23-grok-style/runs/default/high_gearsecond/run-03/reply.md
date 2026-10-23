Immediate retries turned one failure into a burst of extra load, so the dependency never got a chance to recover.

Each failed call became up to six calls in a row (the original plus five retries), all sent at once. During an outage every caller does this at the same time, so traffic multiplies by about six and arrives in lockstep. The dependency is already failing because it is overloaded or restarting. That extra traffic uses its connections, threads, and CPU, keeps queues full, and stretches the outage. The caller suffers too: each request holds a worker and a connection for the whole retry sequence, so its own pools fill up and the failure spreads upstream.

Use a policy that retries less often, spreads the retries out, and stops when the dependency is clearly down.

- Retry only transient failures: connection errors, timeouts, HTTP 429, and HTTP 502/503/504. Do not retry other 4xx responses, and retry non-idempotent writes only when the call is safe to repeat.
- Cap attempts at 2–3, inside an overall deadline. Give up when the deadline is exhausted instead of starting another attempt.
- Wait with exponential backoff and full jitter. For example, sleep a random time between 0 and `min(cap, base * 2^attempt)` (about 100 ms base, 2–5 s cap). Jitter keeps callers from retrying together.
- Honor `Retry-After` on 429 and 503.
- Open a circuit breaker after a run of failures. While it is open, fail fast and send only a few probes. Close it after probes succeed.
- Limit in-flight calls and total retry budget per client so one outage cannot multiply traffic without bound.