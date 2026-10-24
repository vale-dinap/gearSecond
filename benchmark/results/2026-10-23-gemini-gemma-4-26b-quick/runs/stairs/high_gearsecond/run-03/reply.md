To solve this problem, we can use a recurrence relation. Let $F(n)$ be the number of ways to climb a staircase of $n$ steps.

To reach the $n$-th step, your last move must have been either:
1. A single step from the $(n-1)$-th step.
2. A double step from the $(n-2)$-th step.

Therefore, the total number of ways to reach step $n$ is the sum of the ways to reach step $n-1$ and the ways to reach step $n-2$:
$F(n) = F(n-1) + F(n-2)$

This is the Fibonacci sequence. We can determine the starting values:
- For $n=1$: Only one way ([1]). So, $F(1) = 1$.
- For $n=2$: Two ways ([1, 1] or [2]). So, $F(2) = 2$.

Now, we calculate the values up to $n=12$:
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