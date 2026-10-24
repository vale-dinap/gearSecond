To find the number of permutations of {1, 2, 3, 4, 5, 6} where no number is in its original position, we calculate the number of derangements for $n = 6$.

A derangement is a permutation with no fixed points. The number of derangements of $n$ elements, denoted as $D_n$, can be calculated using the recursive formula:
$D_n = (n - 1)(D_{n-1} + D_{n-2})$

Starting with the base cases:
- $D_1 = 0$ (no way to derange a single element)
- $D_2 = 1$ (the only derangement of {1, 2} is {2, 1})

Now, we compute the values up to $n = 6$:
- $D_3 = (3 - 1)(D_2 + D_1) = 2(1 + 0) = 2$
- $D_4 = (4 - 1)(D_3 + D_2) = 3(2 + 1) = 3(3) = 9$
- $D_5 = (5 - 1)(D_4 + D_3) = 4(9 + 2) = 4(11) = 44$
- $D_6 = (6 - 1)(D_5 + D_4) = 5(44 + 9) = 5(53) = 265$

Alternatively, using the inclusion-exclusion formula:
$D_n = n! \sum_{k=0}^{n} \frac{(-1)^k}{k!}$
$D_6 = 720 \left( \frac{1}{0!} - \frac{1}{1!} + \frac{1}{2!} - \frac{1}{3!} + \frac{1}{4!} - \frac{1}{5!} + \frac{1}{6!} \right)$
$D_6 = 720 \left( 1 - 1 + \frac{1}{2} - \frac{1}{6} + \frac{1}{24} - \frac{1}{120} + \frac{1}{720} \right)$
$D_6 = 360 - 120 + 30 - 6 + 1 = 265$

ANSWER: 265