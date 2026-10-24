Let the 4-digit integer be $d_1 d_2 d_3 d_4$.
Constraints:
1. $d_1 + d_2 + d_3 + d_4 = 10$
2. $1 \le d_1 \le 9$
3. $0 \le d_2, d_3, d_4 \le 9$

Substitute $x_1 = d_1 - 1$ (so $x_1 \ge 0$).
Equation becomes:
$(x_1 + 1) + d_2 + d_3 + d_4 = 10$
$x_1 + d_2 + d_3 + d_4 = 9$

Number of non-negative integer solutions using stars and bars ($n=9, k=4$):
$\binom{n+k-1}{k-1} = \binom{9+4-1}{4-1} = \binom{12}{3}$

Calculate $\binom{12}{3}$:
$\frac{12 \times 11 \times 10}{3 \times 2 \times 1} = 2 \times 11 \times 10 = 220$

Check for invalid solutions (violating upper bound constraints):
1. $d_i \le 9$: Since the sum is 9, no variable can exceed 9. All solutions satisfy this.
2. $d_1 \le 9 \implies x_1 \le 8$:
   Invalid if $x_1 \ge 9$.
   Since sum is 9, only $x_1 = 9$ is possible (with $d_2=d_3=d_4=0$).
   This corresponds to $d_1 = 10$, which is not a digit.
   There is exactly 1 such invalid solution.

Subtract invalid cases:
$220 - 1 = 219$

ANSWER: 219