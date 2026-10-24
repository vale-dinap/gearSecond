To find the number of permutations of the set {1, 2, 3, 4, 5, 6} that leave no number in its original position, we need to calculate the number of derangements of 6 elements, denoted as $D_6$.

A derangement is a permutation with no fixed points. The general formula for the number of derangements of $n$ elements is:
$$D_n = n! \sum_{k=0}^{n} \frac{(-1)^k}{k!}$$

For $n = 6$, we substitute into the formula:
$$D_6 = 6! \left( \frac{1}{0!} - \frac{1}{1!} + \frac{1}{2!} - \frac{1}{3!} + \frac{1}{4!} - \frac{1}{5!} + \frac{1}{6!} \right)$$

First, we calculate $6!$:
$$6! = 6 \times 5 \times 4 \times 3 \times 2 \times 1 = 720$$

Next, we expand the terms inside the parentheses:
$$D_6 = 720 \left( \frac{1}{1} - \frac{1}{1} + \frac{1}{2} - \frac{1}{6} + \frac{1}{24} - \frac{1}{120} + \frac{1}{720} \right)$$

The first two terms $\left(1 - 1\right)$ cancel each other out:
$$D_6 = 720 \left( \frac{1}{2} - \frac{1}{6} + \frac{1}{24} - \frac{1}{120} + \frac{1}{720} \right)$$

Now, distribute 720 to each term:
$$D_6 = \frac{720}{2} - \frac{720}{6} + \frac{720}{24} - \frac{720}{120} + \frac{720}{720}$$
$$D_6 = 360 - 120 + 30 - 6 + 1$$

Performing the arithmetic step-by-step:
1. $360 - 120 = 240$
2. $240 + 30 = 270$
3. $270 - 6 = 264$
4. $264 + 1 = 265$

Alternatively, we can use the recurrence relation $D_n = (n-1)(D_{n-1} + D_{n-2})$:
- $D_1 = 0$
- $D_2 = 1$
- $D_3 = 2(1 + 0) = 2$
- $D_4 = 3(2 + 1) = 9$
- $D_5 = 4(9 + 2) = 44$
- $D_6 = 5(44 + 9) = 5(53) = 265$

Both methods give the same result.

ANSWER: 265