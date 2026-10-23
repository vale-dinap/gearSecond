Immediate retries turned one failing dependency into a much larger load spike. Each caller that hit an error sent the same request again right away, up to five more times, so one user action became as many as six calls while the dependency was already down or overloaded. Those extra calls arrived together, filled connection pools and threads on both sides, and kept the dependency from recovering. As soon as it started to come back, the piled-up retries hit it again and knocked it back over.

Use a bounded retry policy with exponential backoff and jitter, and stop sending traffic when the dependency is clearly unhealthy.

- Retry only transient failures: connection errors, timeouts, and `429` / `502` / `503` / `504`. Do not retry other `4xx` responses. Honor `Retry-After` when it is present.
- Retry only idempotent calls, or calls that carry an idempotency key.
- Wait between attempts, for example 100 ms, 200 ms, 400 ms, 800 ms, capped around a few seconds, and add random jitter so clients do not retry in lockstep.
- Keep a small attempt cap, often 2–3 retries, inside the caller's overall deadline so retries cannot stack into a long stall.
- Cap retry volume with a retry budget or token bucket, so retries stay a small fraction of normal traffic.
- Open a circuit breaker after a run of failures and fail fast until a probe succeeds, instead of continuing to hammer the dependency.