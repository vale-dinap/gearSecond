Let $f(n)$ be the number of ways to climb $n$ steps.
Base cases:
$f(1) = 1$
$f(2) = 2$
Recurrence: $f(n) = f(n-1) + f(n-2)$ for $n > 2$.

Calculation:
$f(3) = 2 + 1 = 3$
$f(4) = 3 + 2 = 5$
$f(5) = 5 + 3 = 8$
$f(6) = 8 + 5 = 13$
$f(7) = 13 + 8 = 21$
$f(8) = 21 + 13 = 34$
$f(9) = 34 + 21 = 55$
$f(10) = 55 + 34 = 89$
$f(11) = 89 + 55 = 144$
$f(12) = 144 + 89 = 233$

Check:
$144 + 89 = 233$.
Arithmetic holds.

ANSWER: 233