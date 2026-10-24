This is a derangement problem ($D_n$).

Recurrence relation: $D_n = (n-1)(D_{n-1} + D_{n-2})$.
Base cases: $D_1 = 0$, $D_2 = 1$.

$D_3 = 2(1 + 0) = 2$.
$D_4 = 3(2 + 1) = 9$.
$D_5 = 4(9 + 2) = 44$.
$D_6 = 5(44 + 9) = 5 \times 53 = 265$.

Cross-check via inclusion-exclusion:
Total: $6! = 720$.
$- \binom{6}{1}5! = -720$.
$+ \binom{6}{2}4! = +360$.
$- \binom{6}{3}3! = -120$.
$+ \binom{6}{4}2! = +30$.
$- \binom{6}{5}1! = -6$.
$+ \binom{6}{6}0! = +1$.
Sum: $720 - 720 + 360 - 120 + 30 - 6 + 1 = 265$.

ANSWER: 265