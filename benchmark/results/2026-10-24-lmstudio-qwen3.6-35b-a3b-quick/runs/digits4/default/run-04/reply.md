To find the number of 4-digit positive integers whose digits sum to 10, we represent the integer as $d_1 d_2 d_3 d_4$. The constraints are:
1.  **Leading digit ($d_1$):** Must be between 1 and 9.
2.  **Other digits ($d_2, d_3, d_4$):** Must be between 0 and 9.
3.  **Sum constraint:** $d_1 + d_2 + d_3 + d_4 = 10$.

### Method 1: Stars and Bars with Adjustment
We first transform the constraint $d_1 \ge 1$ by letting $x_1 = d_1 - 1$, where $x_1 \ge 0$. The equation becomes:
$$(x_1 + 1) + d_2 + d_3 + d_4 = 10 \implies x_1 + d_2 + d_3 + d_4 = 9$$

The number of non-negative integer solutions to this equation is given by the Stars and Bars formula $\binom{n+k-1}{k-1}$, where $n=9$ and $k=4$:
$$\binom{9+4-1}{4-1} = \binom{12}{3} = \frac{12 \times 11 \times 10}{3 \times 2 \times 1} = 220$$

However, we must account for the constraint that $d_1 \le 9$. In our transformed equation, $d_1 = x_1 + 1$, so $d_1 \le 9$ implies $x_1 \le 8$. The only solution in the 220 cases where $x_1 > 8$ is $x_1 = 9$ (with $d_2=d_3=d_4=0$), which corresponds to $d_1=10$. This is an invalid digit.
Subtracting this one invalid case: $220 - 1 = 219$.

### Method 2: Case Analysis by Leading Digit
Alternatively, we can sum the possible combinations for the remaining three digits ($d_2, d_3, d_4$) for each valid leading digit $d_1$. The number of non-negative solutions to $d_2 + d_3 + d_4 = S$ is $\binom{S+2}{2}$.

*   If $d_1 = 1$, sum $= 9 \implies \binom{11}{2} = 55$
*   If $d_1 = 2$, sum $= 8 \implies \binom{10}{2} = 45$
*   If $d_1 = 3$, sum $= 7 \implies \binom{9}{2} = 36$
*   If $d_1 = 4$, sum $= 6 \implies \binom{8}{2} = 28$
*   If $d_1 = 5$, sum $= 5 \implies \binom{7}{2} = 21$
*   If $d_1 = 6$, sum $= 4 \implies \binom{6}{2} = 15$
*   If $d_1 = 7$, sum $= 3 \implies \binom{5}{2} = 10$
*   If $d_1 = 8$, sum $= 2 \implies \binom{4}{2} = 6$
*   If $d_1 = 9$, sum $= 1 \implies \binom{3}{2} = 3$

Total: $55 + 45 + 36 + 28 + 21 + 15 + 10 + 6 + 3 = 219$.

ANSWER: 219