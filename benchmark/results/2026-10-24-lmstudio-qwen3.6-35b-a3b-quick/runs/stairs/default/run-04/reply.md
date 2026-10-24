To find the number of ways to climb a staircase of 12 steps with moves of either 1 or 2 steps, we can reason through the problem using a recursive pattern.

Let $W(n)$ represent the number of distinct ways to reach step $n$. 
When you are about to step onto step $n$, your previous step must have been either:
- From step $n-1$ (taking a 1-step move), or
- From step $n-2$ (taking a 2-step move).

Therefore, the total number of ways to reach step $n$ is the sum of the ways to reach the two preceding steps:
$W(n) = W(n-1) + W(n-2)$

Now, we establish the base cases and compute step-by-step:
- $W(0) = 1$ (There's 1 way to be at the ground: do nothing)
- $W(1) = 1$ (Only one way: take a single 1-step)
- $W(2) = W(1) + W(0) = 1 + 1 = 2$ (Ways: 1+1 or 2)
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

This sequence follows the Fibonacci numbers, where each term is the sum of the two preceding terms. By systematically applying the recurrence relation up to the 12th step, we arrive at the total count.

ANSWER: 233