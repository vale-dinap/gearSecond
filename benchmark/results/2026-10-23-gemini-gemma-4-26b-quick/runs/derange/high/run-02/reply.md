To find the number of permutations of the set $\{1, 2, 3, 4, 5, 6\}$ such that no number is left in its original position, we need to calculate the number of derangements of 6 elements, denoted as $D_6$.

A derangement is a permutation $\sigma$ such that $\sigma(i) \neq i$ for all $i$. The formula for the number of derangements of $n$ elements is given by:
$$D_n = n! \sum_{k=0}^{n} \frac{(-1)^k}{k!}$$

For $n = 6$, we have:
$$D_6 = 6! \left( \frac{1}{0!} - \frac{1}{1!} + \frac{1}{2!} - \frac{1}{3!} + \frac{1}{4!} - \frac{1}{5!} + \frac{1}{6!} \right)$$
$$D_6 = 720 \left( 1 - 1 + \frac{1}{2} - \frac{1}{6} + \frac{1}{24} - \frac{1}{120} + \frac{1}{720} \right)$$

Now, we distribute 720 across the terms:
$$D_6 = 720(1) - 720(1) + \frac{720}{2} - \frac{720}{6} + \frac{720}{24} - \frac{720}{120} + \frac{720}{720}$$
$$D_6 = 720 - 720 + 360 - 120 + 30 - 6 + 1$$
$$D_6 = 360 - 120 + 30 - 6 + 1$$
$$D_6 = 240 + 30 - 6 + 1$$
$$D_6 = 270 - 6 + 1$$
$$D_6 = 264 + 1$$
$$D_6 = 265$$

Alternatively, using the recursive formula $D_n = (n-1)(D_{n-1} + D_{n-2})$:
- $D_1 = 0$
- $D_2 = 1$
- $D_3 = (3-1)(D_2 + D_1) = 2(1 + 0) = 2$
- $D_4 = (4-1)(D_3 + D_2) = 3(2 + 1) = 9$
- $D_5 = (5-1)(D_4 + D_3) = 4(9 + 2) = 44$
- $D_6 = (6-1)(D_5 + D_4) = 5(44 + 9) = 5(53) = 265$

Both methods provide the same result.

ANSWER: 265