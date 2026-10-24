To find the number of ways to climb a staircase of 12 steps where each move is either 1 or 2 steps, we can use a recurrence relation.

Let $a_n$ be the number of ways to reach the $n$-th step.
To reach step $n$, the last move must have been either:
1. A 1-step move from step $n-1$.
2. A 2-step move from step $n-2$.

Thus, the recurrence relation is $a_n = a_{n-1} + a_{n-2}$.

First, we determine the base cases:
- $a_1$: The only way to climb 1 step is (1). So, $a_1 = 1$.
- $a_2$: The ways to climb 2 steps are (1, 1) and (2). So, $a_2 = 2$.

Now, we use the recurrence $a_n = a_{n-1} + a_{n-2}$ to find $a_{12}$:
- $a_3 = a_2 + a_1 = 2 + 1 = 3$
- $a_4 = a_3 + a_2 = 3 + 2 = 5$
- $a_5 = a_4 + a_3 = 5 + 3 = 8$
- $a_6 = a_5 + a_4 = 8 + 5 = 13$
- $a_7 = a_6 + a_5 = 13 + 8 = 21$
- $a_8 = a_7 + a_6 = 21 + 13 = 34$
- $a_9 = a_8 + a_7 = 34 + 21 = 55$
- $a_{10} = a_9 + a_8 = 55 + 34 = 89$
- $a_{11} = a_{10} + a_9 = 89 + 55 = 144$
- $a_{12} = a_{11} + a_{10} = 144 + 89 = 233$

Alternatively, we can use the combination method. Let $k$ be the number of 2-step moves. The number of 1-step moves is then $12 - 2k$, and the total number of moves is $k + (12 - 2k) = 12 - k$. The number of ways to arrange these moves is $\binom{12-k}{k}$.
- $k=0: \binom{12}{0} = 1$
- $k=1: \binom{11}{1} = 11$
- $k=2: \binom{10}{2} = \frac{10 \times 9}{2} = 45$
- $k=3: \binom{9}{3} = \frac{9 \times 8 \times 7}{3 \times 2 \times 1} = 84$
- $k=4: \binom{8}{4} = \frac{8 \times 7 \times 6 \times 5}{4 \times 3 \times 2 \times 1} = 70$
- $k=5: \binom{7}{5} = \binom{7}{2} = \frac{7 \times 6}{2} = 21$
- $k=6: \binom{6}{6} = 1$

Summing these: $1 + 11 + 45 + 84 + 70 + 21 + 1 = 233$.

ANSWER: 233