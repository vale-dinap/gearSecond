To count the possible climbs, let  

\[
f(n)= \text{number of different ways to reach step } n .
\]

*Base cases*

- \(f(0)=1\): there is one way to be at the bottom (do nothing).
- \(f(1)=1\): only a single 1‑step move can bring you to the first stair.

*Recurrence*

From any stair \(n>1\) you could have arrived in two ways:

1. From stair \(n-1\) by taking a single step.
2. From stair \(n-2\) by taking a double step.

Hence

\[
f(n)=f(n-1)+f(n-2)\qquad (n>1).
\]

This is exactly the Fibonacci recurrence, with the initial values shifted one place.  
Computing successively:

| \(n\) | \(f(n)\) |
|-------|----------|
| 0 | 1 |
| 1 | 1 |
| 2 | 2 |
| 3 | 3 |
| 4 | 5 |
| 5 | 8 |
| 6 | 13 |
| 7 | 21 |
| 8 | 34 |
| 9 | 55 |
|10 | 89 |
|11 | 144 |
|12 | 233 |

Thus there are **233** distinct ways to climb a staircase of 12 steps when you may take either one or two steps at a time.

ANSWER: 233