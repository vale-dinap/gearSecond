Immediate retries turned one outage into a traffic spike against a service that was already failing.

Each caller request became up to six attempts in a row: the original call plus five retries. While the dependency was down or overloaded, almost every attempt failed, so the client sent about six times the normal request rate at the worst moment. Those extra calls kept sockets, threads, and connection pools busy on both sides, so the dependency had less capacity to recover. When it started accepting traffic again, every client retried at once, with no delay and no spread between them, and the surge knocked it back over.

Use a policy that spends less load when the dependency is unhealthy:

- **Retry only safe failures.** Retry idempotent calls on timeouts, connection errors, and 429/502/503/504. Honor `Retry-After`. Do not retry other 4xx responses.
- **Exponential backoff with full jitter.** For example, wait a random time in `[0, min(cap, base * 2^attempt)]`, with a base around 100–200 ms and a cap around 2–5 s. The growing delay gives the dependency time to recover, and the randomness stops clients from retrying in lockstep.
- **A small attempt budget inside the caller’s deadline.** Two or three retries is usually enough. Stop when the remaining deadline cannot fit another attempt plus its timeout.
- **A circuit breaker.** After a sustained failure rate, open the circuit and fail fast. Probe with a few trial calls, and close only after those succeed. That cuts the amplification while the outage continues.
- **A client-side concurrency limit.** Cap in-flight calls to that dependency so a slow or failing upstream cannot occupy every worker.

The dependency then sees roughly normal traffic plus a little extra, spaced out, and clients stop hammering it once it is clearly down.