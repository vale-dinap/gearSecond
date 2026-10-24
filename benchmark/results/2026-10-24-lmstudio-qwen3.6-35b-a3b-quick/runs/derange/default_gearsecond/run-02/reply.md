This is a derangement problem. We want the number of permutations of $n=6$ elements with no fixed points, denoted $D_6$.

Using the recursive formula $D_n = (n-1)(D_{n-1} + D_{n-2})$:

*   $D_1 = 0$
*   $D_2 = 1$
*   $D_3 = 2(1 + 0) = 2$
*   $D_4 = 3(2 + 1) = 9$
*   $D_5 = 4(9 + 2) = 44$
*   $D_6 = 5(44 + 9) = 5 \times 53 = 265$

Alternatively, using the inclusion-exclusion principle:
$D_6 = 6! \left( \frac{1}{0!} - \frac{1}{1!} + \frac{1}{2!} - \frac{1}{3!} + \frac{1}{4!} - \frac{1}{5!} + \frac{1}{6!} \right)$
$D_6 = 720 \left( 1 - 1 + \frac{1}{2} - \frac{1}{6} + \frac{1}{24} - \frac{1}{120} + \frac{1}{720} \right)$
$D_6 = 360 - 120 + 30 - 6 + 1 = 265$

ANSWER: 265