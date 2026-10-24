To find the number of ways to climb a staircase of 12 steps where each move is either 1 or 2 steps, we can use a recurrence relation.

Let $W(n)$ be the number of ways to climb a staircase of $n$ steps.
- To reach the $n$-th step, your last move could have been a 1-step move from the $(n-1)$-th step.
- Or, your last move could have been a 2-step move from the $(n-2)$-th step.

Therefore, the number of ways to reach step $n$ is the sum of the ways to reach step $n-1$ and the ways to reach step $n-2$:
$W(n) = W(n-1) + W(n-2)$

This is the characteristic recurrence of the Fibonacci sequence. We can find the base cases:
- $W(1)$: To climb 1 step, there is only 1 way: (1). So, $W(1) = 1$.
- $W(2)$: To climb 2 steps, there are 2 ways: (1+1) or (2). So, $W(2) = 2$.

Now we can calculate the values step by step up to $W(12)$:
- $W(1) = 1$
- $W(2) = 2$
- $W(3) = W(2) + W(1) = 2 + 1 = 3$
- $W(4) = W(3) + W(2) = 3 + 2 = 5$
- $W(5) = W(4) + W(3) = 5 + 3 = 8$
- $W(6) = W(5) + W(4) = 8 + 5 = 13$
- $W(7) = W(6) + W(5) = 13 + 8 = 21$
- $W(8) = W(7) + W(6) = 21 + 13 = 34$
- $W(9) = W(8) + W(7) = 34 + 21 = 55$
- $W(10) = W(9) + W(8) = 55 + 34 = 89$
- $W(11) = W(10) + W(9) = 89 + 55 = 144$
- $W(12) = W(11) + W(10) = 144 + 89 = 233$

Alternatively, we can check this using combinations. If $x$ is the number of 2-step moves and $y$ is the number of 1-step moves, then $2x + y = 12$.
- If $x=0, y=12$: $\binom{12}{0} = 1$
- If $x=1, y=10$: $\binom{11}{1} = 11$
- If $x=2, y=8$: $\binom{10}{2} = 45$
- If $x=3, y=6$: $\binom{9}{3} = 84$
- If $x=4, y=4$: $\binom{8}{4} = 70$
- If $x=5, y=2$: $\binom{7}{5} = 21$
- If $x=6, y=0$: $\binom{6}{6} = 1$

Summing these: $1 + 11 + 45 + 84 + 70 + 21 + 1 = 233$.

ANSWER: 233