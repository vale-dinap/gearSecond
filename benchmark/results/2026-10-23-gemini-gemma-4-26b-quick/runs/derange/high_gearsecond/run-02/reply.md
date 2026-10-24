To find the number of permutations where no number remains in its original position, we calculate the number of **derangements** of a set of 6 elements.

A derangement of $n$ elements, denoted as $!n$ or $D_n$, can be calculated using the subfactorial formula:
$$!n = n! \sum_{k=0}^{n} \frac{(-1)^k}{k!}$$

For $n = 6$:
$$!6 = 6! \left( \frac{1}{0!} - \frac{1}{1!} + \frac{1}{2!} - \frac{1}{3!} + \frac{1}{4!} - \frac{1}{5!} + \frac{1}{6!} \right)$$

Calculate each term:
1. $6! = 720$
2. $\frac{1}{0!} = 1$
3. $\frac{1}{1!} = 1$
4. $\frac{1}{2!} = \frac{1}{2}$
5. $\frac{1}{3!} = \frac{1}{6}$
6. $\frac{1}{4!} = \frac{1}{24}$
7. $\frac{1}{5!} = \frac{1}{120}$
8. $\frac{1}{6!} = \frac{1}{720}$

Plug these into the formula:
$$!6 = 720 \left( 1 - 1 + \frac{1}{2} - \frac{1}{6} + \frac{1}{24} - \frac{1}{120} + \frac{1}{720} \right)$$
$$!6 = 720 \left( \frac{1}{2} - \frac{1}{6} + \frac{1}{24} - \frac{1}{120} + \frac{1}{720} \right)$$

Distribute 720:
$$!6 = \frac{720}{2} - \frac{720}{6} + \frac{720}{24} - \frac{720}{120} + \frac{720}{720}$$
$$!6 = 360 - 120 + 30 - 6 + 1$$
$$!6 = 240 + 30 - 6 + 1$$
$$!6 = 270 - 6 + 1$$
$$!6 = 264 + 1$$
$$!6 = 265$$

ANSWER: 265