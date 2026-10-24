To count the different ways to reach the top of a 12‑step staircase when each move can be either one or two steps, we set up a recurrence relation.

Let \(a_n\) denote the number of distinct sequences of 1‑ and 2‑steps that sum to \(n\).

*Base cases*

- \(a_0 = 1\): there is exactly one way to stand on the ground (take no steps).
- \(a_1 = 1\): only a single 1‑step can reach step 1.

*Recurrence*

Consider the last move of any valid sequence that reaches step \(n\).

- If the final move is a 1‑step, the preceding part must bring us to step \(n-1\).  
  There are \(a_{\,n-1}\) such sequences.
- If the final move is a 2‑step, the preceding part must bring us to step \(n-2\).  
  There are \(a_{\,n-2}\) such sequences.

Thus every sequence for \(n\) steps ends either with a 1 or a 2, giving

\[
a_n = a_{\,n-1} + a_{\,n-2}, \qquad n\ge 2.
\]

This is precisely the Fibonacci recurrence. Using the base values above we compute:

| \(n\) | \(a_n\) |
|-------|--------|
| 0     | 1      |
| 1     | 1      |
| 2     | 2      |
| 3     | 3      |
| 4     | 5      |
| 5     | 8      |
| 6     | 13     |
| 7     | 21     |
| 8     | 34     |
| 9     | 55     |
|10     | 89     |
|11     |144     |
|12     |233     |

Therefore, there are **233** different ways to climb a staircase of 12 steps when each move can be either one or two steps.

ANSWER: 233