This problem asks for the number of **derangements** of 6 elements, which are permutations where no element appears in its original position. We can solve this using the Principle of Inclusion-Exclusion.

Start with the total number of permutations of 6 elements:
$6! = 720$

We want to exclude all permutations that have at least one fixed point (a number in its original position), then add back those excluded twice, and so on. The formula is:
$D_n = \sum_{k=0}^{n} (-1)^k \binom{n}{k} (n-k)!$

For $n=6$, we compute each term step-by-step:
- $k=0$: $\binom{6}{0} \cdot 6! = 1 \cdot 720 = 720$
- $k=1$: $-\binom{6}{1} \cdot 5! = -6 \cdot 120 = -720$
- $k=2$: $+\binom{6}{2} \cdot 4! = 15 \cdot 24 = 360$
- $k=3$: $-\binom{6}{3} \cdot 3! = -20 \cdot 6 = -120$
- $k=4$: $+\binom{6}{4} \cdot 2! = 15 \cdot 2 = 30$
- $k=5$: $-\binom{6}{5} \cdot 1! = -6 \cdot 1 = -6$
- $k=6$: $+\binom{6}{6} \cdot 0! = 1 \cdot 1 = 1$

Now sum these alternating terms:
$720 - 720 + 360 - 120 + 30 - 6 + 1$
$= 0 + 360 - 120 + 30 - 6 + 1$
$= 240 + 30 - 6 + 1$
$= 270 - 6 + 1$
$= 265$

As a quick verification, derangements follow the recurrence $D_n = (n-1)(D_{n-1} + D_{n-2})$ with $D_1=0, D_2=1$:
- $D_3 = 2(1+0) = 2$
- $D_4 = 3(2+1) = 9$
- $D_5 = 4(9+2) = 44$
- $D_6 = 5(44+9) = 5 \times 53 = 265$

Both methods confirm the same result.

ANSWER: 265