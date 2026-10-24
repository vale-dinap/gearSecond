Let the 4-digit integer be $d_1 d_2 d_3 d_4$.
Constraints:
1. $d_1 \in \{1, 2, \dots, 9\}$
2. $d_2, d_3, d_4 \in \{0, 1, \dots, 9\}$
3. $d_1 + d_2 + d_3 + d_4 = 10$

Let $x_1 = d_1 - 1$. Then $x_1 \ge 0$.
Equation: $(x_1 + 1) + d_2 + d_3 + d_4 = 10 \implies x_1 + d_2 + d_3 + d_4 = 9$.
We need the number of non-negative integer solutions to this equation.
Using stars and bars formula $\binom{n+k-1}{k-1}$ with $n=9, k=4$:
Total solutions = $\binom{9+4-1}{4-1} = \binom{12}{3}$.

Calculate $\binom{12}{3}$:
$\binom{12}{3} = \frac{12 \times 11 \times 10}{3 \times 2 \times 1} = 2 \times 11 \times 10 = 220$.

Check constraints:
- $d_i \le 9$: Since the sum is 9 and all variables are non-negative, no variable can exceed 9. So this constraint is always satisfied.
- $d_1 \le 9 \implies x_1 \le 8$: We must exclude solutions where $x_1 \ge 9$.
Since sum is 9, only $x_1 = 9$ is possible.
If $x_1 = 9$, then $d_2=d_3=d_4=0$.
This is exactly 1 solution ($d_1=10$, invalid).

Valid solutions = Total - Invalid
$= 220 - 1 = 219$.

ANSWER: 219