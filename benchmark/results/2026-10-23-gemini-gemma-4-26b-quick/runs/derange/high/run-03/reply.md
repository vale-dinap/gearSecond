To find the number of permutations of $\{1, 2, 3, 4, 5, 6\}$ that leave no number in its original position, we need to calculate the number of derangements of 6 elements, denoted as $D_6$ or $!6$.

A derangement is a permutation of the elements of a set such that no element appears in its original position. We can use the recurrence relation for derangements:
$D_n = (n-1)(D_{n-1} + D_{n-2})$ for $n \ge 2$, with base cases $D_0 = 1$ and $D_1 = 0$.

Let's calculate the values for $n=0$ to $n=6$:
1.  $D_0 = 1$
2.  $D_1 = 0$
3.  $D_2 = (2-1)(D_1 + D_0) = 1(0 + 1) = 1$
4.  $D_3 = (3-1)(D_2 + D_1) = 2(1 + 0) = 2$
5.  $D_4 = (4-1)(D_3 + D_2) = 3(2 + 1) = 3(3) = 9$
6.  $D_5 = (5-1)(D_4 + D_3) = 4(9 + 2) = 4(11) = 44$
7.  $D_6 = (6-1)(D_5 + D_4) = 5(44 + 9) = 5(53) = 265$

Alternatively, we can use the inclusion-exclusion formula for derangements:
$D_n = n! \sum_{k=0}^{n} \frac{(-1)^k}{k!}$
For $n=6$:
$D_6 = 6! \left( \frac{1}{0!} - \frac{1}{1!} + \frac{1}{2!} - \frac{1}{3!} + \frac{1}{4!} - \frac{1}{5!} + \frac{1}{6!} \right)$
$D_6 = 720 \left( 1 - 1 + \frac{1}{2} - \frac{1}{6} + \frac{1}{24} - \frac{1}{120} + \frac{1}{720} \right)$
$D_6 = 720 \left( \frac{1}{2} - \frac{1}{6} + \frac{1}{24} - \frac{1}{120} + \frac{1}{720} \right)$
$D_6 = \frac{720}{2} - \frac{720}{6} + \frac{720}{24} - \frac{720}{120} + \frac{720}{720}$
$D_6 = 360 - 120 + 30 - 6 + 1$
$D_6 = 240 + 30 - 6 + 1$
$D_6 = 270 - 6 + 1$
$D_6 = 265$

Both methods yield the same result.

ANSWER: 265