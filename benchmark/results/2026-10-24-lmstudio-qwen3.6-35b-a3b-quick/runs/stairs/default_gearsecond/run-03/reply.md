Let $W(n)$ be the number of ways to reach step $n$.
To reach step $n$, the final move must come from step $n-1$ (1-step) or $n-2$ (2-step).
Recurrence: $W(n) = W(n-1) + W(n-2)$.
Base cases: $W(1) = 1$, $W(2) = 2$.
Compute sequentially:
$W(3) = 2 + 1 = 3$
$W(4) = 3 + 2 = 5$
$W(5) = 5 + 3 = 8$
$W(6) = 8 + 5 = 13$
$W(7) = 13 + 8 = 21$
$W(8) = 21 + 13 = 34$
$W(9) = 34 + 21 = 55$
$W(10) = 55 + 34 = 89$
$W(11) = 89 + 55 = 144$
$W(12) = 144 + 89 = 233$

ANSWER: 233