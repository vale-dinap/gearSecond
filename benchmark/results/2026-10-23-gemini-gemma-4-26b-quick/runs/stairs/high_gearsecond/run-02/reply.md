This is a classic problem that follows the Fibonacci sequence.

Let $F(n)$ be the number of ways to climb $n$ steps.
- To reach step $n$, your last move was either 1 step (from $n-1$) or 2 steps (from $n-2$).
- Therefore, $F(n) = F(n-1) + F(n-2)$.

Base cases:
- $F(1) = 1$ (Move: 1)
- $F(2) = 2$ (Moves: 1+1, 2)

Calculating the sequence up to 12:
- $F(1) = 1$
- $F(2) = 2$
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