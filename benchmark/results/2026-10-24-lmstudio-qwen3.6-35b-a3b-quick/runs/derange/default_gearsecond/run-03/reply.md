This asks for the number of derangements of 6 elements, $D_6$.
Use the recurrence $D_n = (n-1)(D_{n-1} + D_{n-2})$.
Base cases: $D_1 = 0$, $D_2 = 1$.
$D_3 = 2(1 + 0) = 2$
$D_4 = 3(2 + 1) = 9$
$D_5 = 4(9 + 2) = 44$
$D_6 = 5(44 + 9) = 5 \times 53 = 265$

ANSWER: 265