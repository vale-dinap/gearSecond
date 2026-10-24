To find the number of permutations of the set $\{1, 2, 3, 4, 5, 6\}$ where no number is in its original position, we calculate the number of **derangements** for $n=6$. A derangement is a permutation where every element is displaced from its initial position.

We use the **Principle of Inclusion-Exclusion**. We start with the total number of permutations and alternately add and subtract cases where numbers remain in their original positions.

**1. Total Permutations**
The total number of ways to arrange 6 distinct items is $6!$:
$$6! = 720$$

**2. Subtracting Cases with Fixed Points**
We subtract permutations where at least one number is in its original position. We choose 1 position to be fixed and arrange the remaining 5:
$$\binom{6}{1} \times 5! = 6 \times 120 = 720$$
$$720 - 720 = 0$$

**3. Adding Back Over-Subtracted Cases**
Because permutations with two fixed points were subtracted twice, we add them back. We choose 2 positions to be fixed and arrange the remaining 4:
$$\binom{6}{2} \times 4! = 15 \times 24 = 360$$
$$0 + 360 = 360$$

**4. Subtracting Cases with Three Fixed Points**
We subtract permutations where at least three numbers are fixed. We choose 3 positions and arrange the remaining 3:
$$\binom{6}{3} \times 3! = 20 \times 6 = 120$$
$$360 - 120 = 240$$

**5. Adding Back Cases with Four Fixed Points**
We add permutations where at least four numbers are fixed. We choose 4 positions and arrange the remaining 2:
$$\binom{6}{4} \times 2! = 15 \times 2 = 30$$
$$240 + 30 = 270$$

**6. Subtracting Cases with Five Fixed Points**
We subtract permutations where at least five numbers are fixed. We choose 5 positions and arrange the remaining 1:
$$\binom{6}{5} \times 1! = 6 \times 1 = 6$$
$$270 - 6 = 264$$

**7. Adding Back the Case with Six Fixed Points**
Finally, we add the single case where all 6 numbers are in their original positions (the identity permutation):
$$\binom{6}{6} \times 0! = 1 \times 1 = 1$$
$$264 + 1 = 265$$

Alternatively, this can be verified using the recursive derangement formula $D_n = (n-1)(D_{n-1} + D_{n-2})$:
*   $D_1 = 0$
*   $D_2 = 1$
*   $D_3 = 2(1+0) = 2$
*   $D_4 = 3(2+1) = 9$
*   $D_5 = 4(9+2) = 44$
*   $D_6 = 5(44+9) = 5 \times 53 = 265$

ANSWER: 265