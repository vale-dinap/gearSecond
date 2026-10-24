To find the number of 4-digit positive integers whose digits sum to 10, we represent the integer as $d_1d_2d_3d_4$. The digits must satisfy the following conditions:
1.  $d_1 \in \{1, 2, \dots, 9\}$ (the first digit cannot be 0).
2.  $d_2, d_3, d_4 \in \{0, 1, \dots, 9\}$.
3.  $d_1 + d_2 + d_3 + d_4 = 10$.

### 1. Transform the Equation
Let $x_1 = d_1 - 1$. Since $d_1 \ge 1$, $x_1$ is a non-negative integer. Substituting this into the sum equation:
$$(x_1 + 1) + d_2 + d_3 + d_4 = 10$$
$$x_1 + d_2 + d_3 + d_4 = 9$$

### 2. Count Non-Negative Solutions
Using the "stars and bars" method, the number of non-negative integer solutions to $x_1 + d_2 + d_3 + d_4 = 9$ is:
$$\binom{n + k - 1}{k - 1} = \binom{9 + 4 - 1}{4 - 1} = \binom{12}{3}$$
$$\binom{12}{3} = \frac{12 \times 11 \times 10}{3 \times 2 \times 1} = 220$$

### 3. Account for Constraints
We must ensure the digits do not exceed 9.
*   **For $d_2, d_3, d_4$:** Since the total sum is 9 and all digits are non-negative, no digit can possibly exceed 9. These constraints are automatically satisfied.
*   **For $d_1$:** We defined $x_1 = d_1 - 1$. For $d_1$ to be a valid digit ($d_1 \le 9$), $x_1$ must be $\le 8$. In our count of 220 solutions, the only case where $x_1$ exceeds 8 is when $x_1 = 9$ (which implies $d_1 = 10$). This occurs only when $d_2 = d_3 = d_4 = 0$.

Subtracting this single invalid case:
$$220 - 1 = 219$$

ANSWER: 219