When the dependent service went down, every call from this service kept firing five more requests in quick succession.  
- The downstream API received many duplicate traffic bursts, further stressing it and causing its own throttling or failure responses.  
- Each retry also waited for a response that never came; the caller’s timeout expired, propagating errors upstream.  
- The cumulative load made the outage grow instead of shrinking.

A better policy is **exponential back‑off with jitter**:  

1. Limit retries to 3–4 attempts (or a total timeout of ~5 s).  
2. Start at ~100 ms delay, double each time (200 ms, 400 ms…).  
3. Add ±10 % random jitter to avoid synchronized bursts.  
4. Use a per‑request timeout (e.g., 1 s) so that hung calls don’t block the retry loop.

This spreads traffic, gives the downstream service breathing room, and prevents cascading failures.