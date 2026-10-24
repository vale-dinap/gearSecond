To find the number of permutations of {1, 2, 3, 4, 5, 6} where no number remains in its original position, we calculate the number of **derangements** of 6 elements ($D_6$).

A derangement is a permutation with no fixed points. The formula for the number of derangements of $n$ elements ($D_n$) is:
$$D_n = n! \sum_{k=0}^{n} \frac{(-1)^k}{k!}$$

For $n = 6$:
$$D_6 = 6! \left( \frac{1}{0!} - \frac{1}{1!} + \frac{1}{2!} - \frac{1}{3!} + \frac{1}{4!} - \frac{1}{5!} + \frac{1}{6!} \right)$$

Expanding the terms:
$$D_6 = 720 \left( 1 - 1 + \frac{1}{2} - \frac{1}{6} + \frac{1}{24} - \frac{1}{120} + \frac{1}{720} \right)$$

Distributing 720:
$$D_6 = 720(1) - 720(1) + \frac{720}{2} - \frac{720}{6} + \frac{720}{24} - \frac{720}{120} + \frac{720}{720}$$
$$D_6 = 720 - 720 + 360 - 120 + 30 - 6 + 1$$

Calculating the sum:
$$360 - 120 = 240$$
$$240 + 30 = 270$$
$$270 - 6 = 264$$
$$264 + 1 = 265$$

Alternatively, using the recursive formula $D_n = (n-1)(D_{n-1} + D_{n-2})$:
$D_1 = 0$
$D_2 = 1$
$D_3 = 2(1 + 0) = 2$
$D_4 = 3(2 + 1) = 9$
$D_5 = 4(9 + 2) = 44$
$D_6 = 5(44 + 9) = 5(53) = 265$

ANSWER: 265