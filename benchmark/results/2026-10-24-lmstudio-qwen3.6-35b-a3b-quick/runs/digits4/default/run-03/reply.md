To find the number of 4-digit positive integers whose digits sum to 10, we represent the integer as $d_1 d_2 d_3 d_4$. The constraints are:
1.  **Leading digit:** $d_1 \in \{1, 2, \dots, 9\}$
2.  **Other digits:** $d_2, d_3, d_4 \in \{0, 1, \dots, 9\}$
3.  **Sum:** $d_1 + d_2 + d_3 + d_4 = 10$

### 1. Transforming the Equation
To simplify the calculation, we account for the leading digit constraint by setting $d_1' = d_1 - 1$. Since $d_1 \ge 1$, $d_1'$ must be a non-negative integer ($d_1' \ge 0$). Substituting this into the sum equation:
$$(d_1' + 1) + d_2 + d_3 + d_4 = 10$$
$$d_1' + d_2 + d_3 + d_4 = 9$$

Now, we are looking for the number of non-negative integer solutions to this equation.

### 2. Applying Stars and Bars
The number of solutions to an equation $x_1 + \dots + x_k = n$ in non-negative integers is given by the formula $\binom{n+k-1}{k-1}$.
*   $n = 9$ (the sum)
*   $k = 4$ (the number of variables: $d_1', d_2, d_3, d_4$)

Total solutions = $\binom{9+4-1}{4-1} = \binom{12}{3}$.
$$\binom{12}{3} = \frac{12 \times 11 \times 10}{3 \times 2 \times 1} = 220$$

### 3. Checking Upper Bound Constraints
We must ensure that no digit exceeds 9.
*   **For $d_2, d_3, d_4$:** In the equation $d_1' + d_2 + d_3 + d_4 = 9$, no variable can exceed 9 because the total sum is 9.
*   **For $d_1$:** The original digit is $d_1 = d_1' + 1$. If $d_1' = 9$, then $d_1 = 10$, which is not a valid digit. 

The only case where $d_1' = 9$ occurs when $d_2 = d_3 = d_4 = 0$. This corresponds to the single invalid solution $(10, 0, 0, 0)$.

### 4. Final Calculation
Subtracting the single invalid case from the total count:
$$220 - 1 = 219$$

ANSWER: 219