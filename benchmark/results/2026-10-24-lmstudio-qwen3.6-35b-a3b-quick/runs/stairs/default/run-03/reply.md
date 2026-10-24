This is a classic combinatorial problem that follows the Fibonacci sequence. Let $f(n)$ represent the number of ways to climb $n$ steps.

To reach step $n$, your final move must have been either:
- A 1-step move from step $n-1$, or
- A 2-step move from step $n-2$

This gives us the recurrence relation:  
$f(n) = f(n-1) + f(n-2)$

We start with the base cases:
- $f(1) = 1$ (just one way: `1`)
- $f(2) = 2$ (two ways: `1+1` or `2`)

Now we compute step-by-step up to 12:
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

Thus, there are 233 distinct sequences of 1-step and 2-step moves that sum to 12.

ANSWER: 233