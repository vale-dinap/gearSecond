To find the number of 4-digit positive integers whose digits sum to 10, we can represent the integer as $d_1d_2d_3d_4$, where $d_1$ is the first digit and $d_2, d_3, d_4$ are the subsequent digits.

The conditions for the digits are:
1. $d_1 + d_2 + d_3 + d_4 = 10$
2. $1 \le d_1 \le 9$ (since it is a 4-digit number, the first digit cannot be 0)
3. $0 \le d_2, d_3, d_4 \le 9$

To simplify the first condition, let $x_1 = d_1 - 1$. Since $1 \le d_1 \le 9$, it follows that $0 \le x_1 \le 8$.
Substituting $d_1 = x_1 + 1$ into the sum equation:
$(x_1 + 1) + d_2 + d_3 + d_4 = 10$
$x_1 + d_2 + d_3 + d_4 = 9$

Now we need to find the number of non-negative integer solutions to $x_1 + d_2 + d_3 + d_4 = 9$, subject to the constraint $x_1 \le 8$.

First, we calculate the total number of non-negative integer solutions to $x_1 + d_2 + d_3 + d_4 = 9$ using the stars and bars formula, which is $\binom{n+k-1}{k-1}$, where $n=9$ and $k=4$:
$\binom{9+4-1}{4-1} = \binom{12}{3}$
$\binom{12}{3} = \frac{12 \times 11 \times 10}{3 \times 2 \times 1} = 2 \times 11 \times 10 = 220$

Next, we check if any of these solutions violate the constraints. The only constraint we have not fully accounted for is $x_1 \le 8$. 
A solution violates $x_1 \le 8$ if $x_1 \ge 9$. 
Since the total sum is 9, the only way $x_1$ can be $\ge 9$ is if $x_1 = 9$. 
If $x_1 = 9$, then $d_2 = 0, d_3 = 0, \text{ and } d_4 = 0$.
This corresponds to $d_1 = x_1 + 1 = 10$, which is not a valid digit for a 4-digit number.

All other variables ($d_2, d_3, d_4$) are naturally constrained to be $\le 9$ because their sum is 9.

Subtracting the single invalid case where $x_1 = 9$:
$220 - 1 = 219$

ANSWER: 219