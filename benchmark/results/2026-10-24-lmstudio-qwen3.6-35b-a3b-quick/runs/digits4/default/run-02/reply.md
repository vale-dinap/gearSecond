To find the number of 4-digit positive integers whose digits sum to 10, we represent the integer as $d_1 d_2 d_3 d_4$. The constraints are:
1.  **Sum of digits:** $d_1 + d_2 + d_3 + d_4 = 10$
2.  **First digit:** $d_1 \in \{1, 2, \dots, 9\}$
3.  **Other digits:** $d_2, d_3, d_4 \in \{0, 1, \dots, 9\}$

### 1. Reformulate the Equation
Since $d_1 \ge 1$, we define a new variable $x_1 = d_1 - 1$ (where $x_1 \ge 0$). Substituting this into the sum equation:
$(x_1 + 1) + d_2 + d_3 + d_4 = 10$
$x_1 + d_2 + d_3 + d_4 = 9$

We now need to find the number of non-negative integer solutions to this equation.

### 2. Apply Stars and Bars
The number of non-negative solutions to $x_1 + x_2 + x_3 + x_4 = n$ is given by the formula $\binom{n+k-1}{k-1}$, where $n=9$ and $k=4$ (the number of variables):
$$\binom{9 + 4 - 1}{4 - 1} = \binom{12}{3}$$
Calculating the binomial coefficient:
$$\binom{12}{3} = \frac{12 \times 11 \times 10}{3 \times 2 \times 1} = 2 \times 11 \times 10 = 220$$

### 3. Check for Digit Constraints
The variables $d_1, d_2, d_3, d_4$ must all be single digits ($\le 9$).
*   **For $d_2, d_3, d_4$:** Since the sum of all variables is 10 and $d_1 \ge 1$, it is impossible for any of these variables to reach 10.
*   **For $d_1$:** $d_1 = x_1 + 1$. In the Stars and Bars calculation, $x_1$ can be at most 9. If $x_1 = 9$, then $d_1 = 10$, which is not a valid digit. This occurs only when $x_1=9$ and $d_2=d_3=d_4=0$ (representing the number 10000).

Subtracting this single invalid case:
$$220 - 1 = 219$$

### 4. Verification
We can verify this by summing the number of solutions for each possible value of $d_1$ (from 1 to 9). For a fixed $d_1$, the remaining sum $S = 10 - d_1$ must be distributed among $d_2, d_3, d_4$. The number of ways is $\binom{S+2}{2}$:
*   $d_1=1 (S=9): \binom{11}{2} = 55$
*   $d_1=2 (S=8): \binom{10}{2} = 45$
*   $d_1=3 (S=7): \binom{9}{2} = 36$
*   $d_1=4 (S=6): \binom{8}{2} = 28$
*   $d_1=5 (S=5): \binom{7}{2} = 21$
*   $d_1=6 (S=4): \binom{6}{2} = 15$
*   $d_1=7 (S=3): \binom{5}{2} = 10$
*   $d_1=8 (S=2): \binom{4}{2} = 6$
*   $d_1=9 (S=1): \binom{3}{2} = 3$

Total sum: $55 + 45 + 36 + 28 + 21 + 15 + 10 + 6 + 3 = 219$.

ANSWER: 219