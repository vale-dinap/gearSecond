Retries immediately up to five times  
add traffic when dependency is down  
overloads downstream queues, causes back‑pressure  
increases latency for all clients  
exacerbates outage by stressing shared resources  

Use exponential backoff with jitter  
start 100 ms, double each retry, max 2 s  
cap total attempts at three or four  
add per‑request timeout of 500 ms  
enable circuit breaker after N failures  
reset after successful call.