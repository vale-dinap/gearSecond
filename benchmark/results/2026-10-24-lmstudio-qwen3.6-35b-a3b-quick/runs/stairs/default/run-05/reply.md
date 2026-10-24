This is a classic combinatorial problem that follows the Fibonacci sequence. Here's the step-by-step reasoning:

Let $f(n)$ represent the number of distinct ways to reach step $n$. To arrive at step $n$, your last move must have been either:
- A 1-step move from step $n-1$
- A 2-step move from step $n-2$

This gives us the recurrence relation:
$f(n) = f(n-1) + f(n-2)$

We start with the base cases:
- $f(0) = 1$ (one way to be at the ground: take no steps)
- $f(1) = 1$ (one way: take a single 1-step)

Now, we compute sequentially up to 12:
- $f(2) = f(1) + f(0) = 1 + 1 = 2$
- $f(3) = f(2) + f(1) = 2 + 1 = 3$
- $f(4) = f(3) + f(2) = 3 + 2 = 5$
- $f(5) = f(4) + f(3) = 5 + 3 = 8$
- $f(6) = f(5) + f(4) = 8 + 5 = 13$
- $f(7) = f(6) + f(5) = 13 + 8 = 21$
- $f(8) = f(7) + f(6) = 21 + 13 = 34$
- $f(9) = f(8) + f(7) = 34 + 21 = 55$
- $f(10) = f(9) + f(8) = 55 + 34 = 89$
- $f(11) = f(10) + f(9) = 89 + 55 = 144$
- $f(12) = f(11) + f(10) = 144 + 89 = 233$

(As a quick verification, you can also sum the combinations of 1-steps and 2-steps for each possible number of 2-steps taken, from 0 to 6: $\binom{12}{0} + \binom{11}{1} + \binom{10}{2} + \binom{9}{3} + \binom{8}{4} + \binom{7}{5} + \binom{6}{6} = 1 + 11 + 45 + 84 + 70 + 21 + 1 = 233$. Both methods agree.)

ANSWER: 233