To find the number of 4-digit positive integers whose digits sum to 10, we let the digits be $d_1, d_2, d_3, d_4$. The conditions are:
1. $1 \le d_1 \le 9$
2. $0 \le d_2 \le 9$
3. $0 \le d_3 \le 9$
4. $0 \le d_4 \le 9$
5. $d_1 + d_2 + d_3 + d_4 = 10$

Let $d_1' = d_1 - 1$. The equation becomes:
$(d_1' + 1) + d_2 + d_3 + d_4 = 10$
$d_1' + d_2 + d_3 + d_4 = 9$
where $d_1', d_2, d_3, d_4 \ge 0$.

The number of non-negative integer solutions to $x_1 + x_2 + x_3 + x_4 = n$ is given by the stars and bars formula $\binom{n+k-1}{k-1}$. Here $n=9$ and $k=4$:
$\text{Number of solutions} = \binom{9+4-1}{4-1} = \binom{12}{3} = \frac{12 \times 11 \times 10}{3 \times 2 \times 1} = 220$.

We must now ensure that all solutions satisfy the digit constraints. The constraints for $d_2, d_3,$ and $d_4$ are $d_i \le 9$. Since their sum is at most 9, these constraints are automatically satisfied for all solutions.
The constraint for $d_1$ is $1 \le d_1 \le 9$, which implies $0 \le d_1' \le 8$.
The only solution in our count of 220 that violates $d_1' \le 8$ is the case where $d_1' = 9$.
If $d_1' = 9$, then $d_2 = d_3 = d_4 = 0$.
This corresponds to the integer with digits $d_1 = 10, d_2 = 0, d_3 = 0, d_4 = 0$, which is not a 4-digit integer because 10 is not a digit.

Subtracting this one invalid case from our total:
$220 - 1 = 219$.

Alternatively, we can sum the number of solutions for each possible value of $d_1$:
- If $d_1=1$, $d_2+d_3+d_4=9 \implies \binom{9+3-1}{2} = \binom{11}{2} = 55$
- If $d_1=2$, $d_2+d_3+d_4=8 \implies \binom{8+3-1}{2} = \binom{10}{2} = 45$
- If $d_1=3$, $d_2+d_3+d_4=7 \implies \binom{7+3-1}{2} = \binom{9}{2} = 36$
- If $d_1=4$, $d_2+d_3+d_4=6 \implies \binom{6+3-1}{2} = \binom{8}{2} = 28$
- If $d_1=5$, $d_2+d_3+d_4=5 \implies \binom{5+3-1}{2} = \binom{7}{2} = 21$
- If $d_1=6$, $d_2+d_3+d_4=4 \implies \binom{4+3-1}{2} = \binom{6}{2} = 15$
- If $d_1=7$, $d_2+d_3+d_4=3 \implies \binom{3+3-1}{2} = \binom{5}{2} = 10$
- If $d_1=8$, $d_2+d_3+d_4=2 \implies \binom{2+3-1}{2} = \binom{4}{2} = 6$
- If $d_1=9$, $d_2+d_3+d_4=1 \implies \binom{1+3-1}{2} = \binom{3}{2} = 3$

Total: $55 + 45 + 36 + 28 + 21 + 15 + 10 + 6 + 3 = 219$.

ANSWER: 219