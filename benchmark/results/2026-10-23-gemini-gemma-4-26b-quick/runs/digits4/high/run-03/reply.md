To find the number of 4-digit positive integers whose digits sum to 10, let the integer be represented by its digits $d_1, d_2, d_3, d_4$. The conditions are:
1. $d_1 \in \{1, 2, \dots, 9\}$
2. $d_2, d_3, d_4 \in \{0, 1, \dots, 9\}$
3. $d_1 + d_2 + d_3 + d_4 = 10$

We can simplify the first condition by letting $d_1' = d_1 - 1$, where $d_1' \in \{0, 1, \dots, 8\}$.
Substituting $d_1 = d_1' + 1$ into the sum equation gives:
$(d_1' + 1) + d_2 + d_3 + d_4 = 10$
$d_1' + d_2 + d_3 + d_4 = 9$

We need to find the number of non-negative integer solutions to this equation, subject to the constraints $d_1' \le 8$ and $d_2, d_3, d_4 \le 9$.
First, we find the total number of non-negative integer solutions to $d_1' + d_2 + d_3 + d_4 = 9$ using the stars and bars formula:
$\text{Number of solutions} = \binom{n+k-1}{k-1} = \binom{9+4-1}{4-1} = \binom{12}{3}$
$\binom{12}{3} = \frac{12 \times 11 \times 10}{3 \times 2 \times 1} = 220$

Next, we subtract the cases that violate our constraints. 
The constraints on $d_2, d_3,$ and $d_4$ are that they must be at most 9. However, in the equation $d_1' + d_2 + d_3 + d_4 = 9$, no variable can exceed 9, so these constraints are automatically satisfied.
The only constraint that can be violated is $d_1' \le 8$. If $d_1'$ were greater than 8, the only possibility (given the sum is 9) is $d_1' = 9$.
If $d_1' = 9$, then $d_2 = d_3 = d_4 = 0$. This corresponds to the case where $d_1 = d_1' + 1 = 10$, which is not a single digit.
There is exactly 1 such case: $(10, 0, 0, 0)$.

Subtracting this one invalid case from the total number of solutions:
$220 - 1 = 219$

Alternatively, we can sum the number of solutions for each possible value of $d_1$:
- If $d_1 = 1$, $d_2+d_3+d_4 = 9 \implies \binom{9+3-1}{3-1} = \binom{11}{2} = 55$
- If $d_1 = 2$, $d_2+d_3+d_4 = 8 \implies \binom{8+3-1}{3-1} = \binom{10}{2} = 45$
- If $d_1 = 3$, $d_2+d_3+d_4 = 7 \implies \binom{7+3-1}{3-1} = \binom{9}{2} = 36$
- If $d_1 = 4$, $d_2+d_3+d_4 = 6 \implies \binom{6+3-1}{3-1} = \binom{8}{2} = 28$
- If $d_1 = 5$, $d_2+d_3+d_4 = 5 \implies \binom{5+3-1}{3-1} = \binom{7}{2} = 21$
- If $d_1 = 6$, $d_2+d_3+d_4 = 4 \implies \binom{4+3-1}{3-1} = \binom{6}{2} = 15$
- If $d_1 = 7$, $d_2+d_3+d_4 = 3 \implies \binom{3+3-1}{3-1} = \binom{5}{2} = 10$
- If $d_1 = 8$, $d_2+d_3+d_4 = 2 \implies \binom{2+3-1}{3-1} = \binom{4}{2} = 6$
- If $d_1 = 9$, $d_2+d_3+d_4 = 1 \implies \binom{1+3-1}{3-1} = \binom{3}{2} = 3$

Summing these up: $55 + 45 + 36 + 28 + 21 + 15 + 10 + 6 + 3 = 219$.

ANSWER: 219