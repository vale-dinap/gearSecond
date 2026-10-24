To find the number of 4-digit positive integers where the digits sum to 10, we represent the integer as $d_1 d_2 d_3 d_4$. The constraints are:
1.  $d_1 \in \{1, 2, \dots, 9\}$ (the first digit cannot be 0).
2.  $d_2, d_3, d_4 \in \{0, 1, \dots, 9\}$.
3.  $d_1 + d_2 + d_3 + d_4 = 10$.

### 1. Transform the Equation
To use the "Stars and Bars" combinatorial method, we adjust the first digit to be non-negative:
Let $x_1 = d_1 - 1$. Since $d_1 \ge 1$, then $x_1 \ge 0$.
Substituting $d_1 = x_1 + 1$ into the sum equation:
$(x_1 + 1) + d_2 + d_3 + d_4 = 10$
$x_1 + d_2 + d_3 + d_4 = 9$

### 2. Calculate Total Non-negative Solutions
The number of non-negative integer solutions to $x_1 + d_2 + d_3 + d_4 = 9$ is given by the formula $\binom{n+k-1}{k-1}$, where $n=9$ and $k=4$:
$$\binom{9 + 4 - 1}{4 - 1} = \binom{12}{3} = \frac{12 \times 11 \times 10}{3 \times 2 \times 1} = 220$$

### 3. Apply Upper Bound Constraints
We must ensure no digit exceeds 9.
*   **For $d_2, d_3, d_4$:** Since their sum is 9, none can exceed 9. These constraints are automatically satisfied.
*   **For $d_1$:** We require $d_1 \le 9$, which means $x_1 + 1 \le 9$, or $x_1 \le 8$.
In the 220 solutions found, the only case where $x_1 > 8$ is when $x_1 = 9$ (which forces $d_2=d_3=d_4=0$). This corresponds to $d_1 = 10$, which is an invalid digit.

Subtracting this single invalid case:
$220 - 1 = 219$

### 4. Verification (Manual Summation)
We can also verify by iterating through possible values of $d_1$:
*   If $d_1 = 1$, $d_2+d_3+d_4 = 9 \implies \binom{11}{2} = 55$ solutions.
*   If $d_1 = 2$, $d_2+d_3+d_4 = 8 \implies \binom{10}{2} = 45$ solutions.
*   If $d_1 = 3$, $d_2+d_3+d_4 = 7 \implies \binom{9}{2} = 36$ solutions.
*   If $d_1 = 4$, $d_2+d_3+d_4 = 6 \implies \binom{8}{2} = 28$ solutions.
*   If $d_1 = 5$, $d_2+d_3+d_4 = 5 \implies \binom{7}{2} = 21$ solutions.
*   If $d_1 = 6$, $d_2+d_3+d_4 = 4 \implies \binom{6}{2} = 15$ solutions.
*   If $d_1 = 7$, $d_2+d_3+d_4 = 3 \implies \binom{5}{2} = 10$ solutions.
*   If $d_1 = 8$, $d_2+d_3+d_4 = 2 \implies \binom{4}{2} = 6$ solutions.
*   If $d_1 = 9$, $d_2+d_3+d_4 = 1 \implies \binom{3}{2} = 3$ solutions.

Summing these: $55 + 45 + 36 + 28 + 21 + 15 + 10 + 6 + 3 = 219$.

ANSWER: 219