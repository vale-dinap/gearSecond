To reach step 12 using steps of size 1 or 2, each path can be described by a sequence of “1” and “2” whose sum is 12.

Let \(F(n)\) denote the number of ways to climb \(n\) steps.  
If the first move is 1‑step, the remaining problem is climbing \(n-1\) steps: \(F(n-1)\).  
If the first move is 2‑steps, the rest is climbing \(n-2\) steps: \(F(n-2)\).

Thus \(F(n)=F(n-1)+F(n-2)\), with base cases  
\(F(0)=1\) (stay at bottom), \(F(1)=1\) (one 1‑step).

Compute iteratively:

| n | F(n) |
|---|------|
|0|1|
|1|1|
|2|2|
|3|3|
|4|5|
|5|8|
|6|13|
|7|21|
|8|34|
|9|55|
|10|89|
|11|144|
|12|233|

So there are 233 distinct ways to climb the staircase.  
ANSWER: 233