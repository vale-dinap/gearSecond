To find the number of ways to climb a staircase of $n$ steps using moves of 1 or 2 steps, we can use a recurrence relation.

Let $F(n)$ be the number of ways to reach step $n$.
- To reach step $n$, the last move must have been either a 1-step move from step $n-1$ or a 2-step move from step $n-2$.
- Therefore, $F(n) = F(n-1) + F(n-2)$.

This is the Fibonacci sequence. We establish the base cases:
- $F(1) = 1$ (Sequence: {1})
- $F(2) = 2$ (Sequences: {1,1}, {2})

Now, we calculate up to $n=12$:
- $F(3) = 1 + 2 = 3$
- $F(4) = 2 + 3 = 5$
- $F(5) = 3 + 5 = 8$
- $F(6) = 5 + 8 = 13$
- $F(7) = 8 + 13 = 21$
- $F(8) = 13 + 21 = 34$
- $F(9) = 21 + 34 = 55$
- $F(10) = 34 + 55 = 89$
- $F(11) = 55 + 89 = 144$
- $F(12) = 89 + 144 = 233$

ANSWER: 233