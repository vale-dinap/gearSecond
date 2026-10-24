To find the number of ways to climb a staircase of 12 steps where each move is either 1 or 2 steps, we can use a recurrence relation.

Let $W(n)$ be the number of ways to climb a staircase of $n$ steps.
1.  To reach the $n$-th step, the last move could have been a 1-step move from the $(n-1)$-th step or a 2-step move from the $(n-2)$-th step.
2.  Therefore, the total number of ways to reach the $n$-th step is the sum of the ways to reach the $(n-1)$-th step and the ways to reach the $(n-2)$-th step:
    $W(n) = W(n-1) + W(n-2)$

This is the Fibonacci sequence. Let's determine the base cases:
-   For $n=1$: There is only 1 way (1). Thus, $W(1) = 1$.
-   For $n=2$: There are 2 ways (1, 1) or (2). Thus, $W(2) = 2$.

Now, we can calculate $W(n)$ for $n=3$ to $n=12$:
-   $W(3) = W(2) + W(1) = 2 + 1 = 3$
-   $W(4) = W(3) + W(2) = 3 + 2 = 5$
-   $W(5) = W(4) + W(3) = 5 + 3 = 8$
-   $W(6) = W(5) + W(4) = 8 + 5 = 13$
-   $W(7) = W(6) + W(5) = 13 + 8 = 21$
-   $W(8) = W(7) + W(6) = 21 + 13 = 34$
-   $W(9) = W(8) + W(7) = 34 + 21 = 55$
-   $W(10) = W(9) + W(8) = 55 + 34 = 89$
-   $W(11) = W(10) + W(9) = 89 + 55 = 144$
-   $W(12) = W(11) + W(10) = 144 + 89 = 233$

Alternatively, we can use the combination formula where $k$ is the number of 2-step moves. The number of 1-step moves will be $12 - 2k$, and the total number of moves will be $k + (12 - 2k) = 12 - k$. The number of ways to arrange these moves is $\binom{12-k}{k}$.
-   $k=0: \binom{12}{0} = 1$
-   $k=1: \binom{11}{1} = 11$
-   $k=2: \binom{10}{2} = 45$
-   $k=3: \binom{9}{3} = 84$
-   $k=4: \binom{8}{4} = 70$
-   $k=5: \binom{7}{5} = 21$
-   $k=6: \binom{6}{6} = 1$

Summing these: $1 + 11 + 45 + 84 + 70 + 21 + 1 = 233$.

ANSWER: 233