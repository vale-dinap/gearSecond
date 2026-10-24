Let digits be $d_1 d_2 d_3 d_4$.
$d_1 \in \{1..9\}$, $d_2,d_3,d_4 \in \{0..9\}$.
Equation: $d_1 + d_2 + d_3 + d_4 = 10$.

Substitute $x_1 = d_1 - 1 \ge 0$.
$x_1 + d_2 + d_3 + d_4 = 9$.

Non-negative solutions via stars & bars:
$\binom{9+4-1}{4-1} = \binom{12}{3} = \frac{12 \times 11 \times 10}{6} = 220$.

Check upper bounds:
$d_2,d_3,d_4 \le 9$ automatically satisfied (sum is 9, $x_1 \ge 0$).
$x_1 \le 8$ (since $d_1 \le 9$). Violation: $x_1 \ge 9 \Rightarrow x_1=9$, others 0. Exactly 1 invalid case ($d_1=10$).

Valid count: $220 - 1 = 219$.

Cross-check by summing cases for $d_1$:
$d_1=1 \to d_2+d_3+d_4=9 \Rightarrow \binom{11}{2}=55$
$d_1=2 \to 8 \Rightarrow \binom{10}{2}=45$
$d_1=3 \to 7 \Rightarrow \binom{9}{2}=36$
$d_1=4 \to 6 \Rightarrow \binom{8}{2}=28$
$d_1=5 \to 5 \Rightarrow \binom{7}{2}=21$
$d_1=6 \to 4 \Rightarrow \binom{6}{2}=15$
$d_1=7 \to 3 \Rightarrow \binom{5}{2}=10$
$d_1=8 \to 2 \Rightarrow \binom{4}{2}=6$
$d_1=9 \to 1 \Rightarrow \binom{3}{2}=3$
Sum: $55+45+36+28+21+15+10+6+3 = 219$. Matches.

ANSWER: 219