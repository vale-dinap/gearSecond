To find the number of 4-digit positive integers whose digits sum to 10, let the digits be $d_1, d_2, d_3, d_4$.
The conditions are:
1. $d_1 + d_2 + d_3 + d_4 = 10$
2. $d_1 \in \{1, 2, 3, 4, 5, 6, 7, 8, 9\}$ (since it's a 4-digit number)
3. $d_2, d_3, d_4 \in \{0, 1, 2, 3, 4, 5, 6, 7, 8, 9\}$

We can substitute $x_1 = d_1 - 1$ to change the range of $d_1$ to $x_1 \in \{0, 1, \dots, 8\}$.
The equation becomes:
$(x_1 + 1) + d_2 + d_3 + d_4 = 10$
$x_1 + d_2 + d_3 + d_4 = 9$

The constraints are:
$0 \le x_1 \le 8$
$0 \le d_2 \le 9$
$0 \le d_3 \le 9$
$0 \le d_4 \le 9$

First, we find the number of non-negative integer solutions to $x_1 + d_2 + d_3 + d_4 = 9$ using the stars and bars formula, which is $\binom{n+k-1}{k-1}$ where $n=9$ and $k=4$:
$\text{Total solutions} = \binom{9+4-1}{4-1} = \binom{12}{3} = \frac{12 \times 11 \times 10}{3 \times 2 \times 1} = 2 \times 11 \times 10 = 220$

Next, we subtract the solutions that violate the constraints.
The constraint $x_1 \le 8$ is violated if $x_1 \ge 9$. Since the total sum is 9, the only case is $x_1 = 9$ and $d_2 = d_3 = d_4 = 0$. This corresponds to $d_1 = 10$, which is not a single digit. This gives 1 case.
The constraints $d_2 \le 9$, $d_3 \le 9$, and $d_4 \le 9$ cannot be violated because their sum is at most 9.

Thus, the number of valid 4-digit integers is:
$220 - 1 = 219$

Alternatively, we can sum the number of solutions for each possible value of $d_1$:
If $d_1=1$, $d_2+d_3+d_4=9 \implies \binom{9+2}{2} = \binom{11}{2} = 55$
If $d_1=2$, $d_2+d_3+d_4=8 \implies \binom{8+2}{2} = \binom{10}{2} = 45$
If $d_1=3$, $d_2+d_3+d_4=7 \implies \binom{7+2}{2} = \binom{9}{2} = 36$
If $d_1=4$, $d_2+d_3+d_4=6 \implies \binom{6+2}{2} = \binom{8}{2} = 28$
If $d_1=5$, $d_2+d_3+d_4=5 \implies \binom{5+2}{2} = \binom{7}{2} = 21$
If $d_1=6$, $d_2+d_3+d_4=4 \implies \binom{4+2}{2} = \binom{6}{2} = 15$
If $d_1=7$, $d_2+d_3+d_4=3 \implies \binom{3+2}{2} = \binom{5}{2} = 10$
If $d_1=8$, $d_2+d_3+d_4=2 \implies \binom{2+2}{2} = \binom{4}{2} = 6$
If $d_1=9$, $d_2+d_3+d_4=1 \implies \binom{1+2}{2} = \binom{3}{2} = 3$

Summing these: $55 + 45 + 36 + 28 + 21 + 15 + 10 + 6 + 3 = 219$

ANSWER: 219