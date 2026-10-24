Let the integer be $d_1 d_2 d_3 d_4$.
$d_1 + d_2 + d_3 + d_4 = 10$.
$d_1 \in \{1, \dots, 9\}$, $d_i \in \{0, \dots, 9\}$ for $i \ge 2$.
Let $x_1 = d_1 - 1$. Then $x_1 \in \{0, \dots, 8\}$.
Equation: $(x_1 + 1) + d_2 + d_3 + d_4 = 10 \implies x_1 + d_2 + d_3 + d_4 = 9$.
Number of non-negative solutions to $x_1 + d_2 + d_3 + d_4 = 9$ is $\binom{9+4-1}{4-1} = \binom{12}{3}$.
$\binom{12}{3} = \frac{12 \times 11 \times 10}{6} = 220$.
Constraints check:
$d_i \le 9$ for $i \ge 2$ is always true since sum is 9.
$x_1 \le 8$ is violated only if $x_1 \ge 9$.
Since sum is 9, $x_1 \ge 9 \implies x_1 = 9, d_2=d_3=d_4=0$.
This is exactly 1 invalid case ($d_1 = 10$).
Valid solutions: $220 - 1 = 219$.

ANSWER: 219