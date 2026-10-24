To find the number of 4-digit positive integers whose digits sum to 10, we can use the stars and bars method.

Let the four digits be $d_1, d_2, d_3,$ and $d_4$.
The conditions are:
1. $d_1 + d_2 + d_3 + d_4 = 10$
2. $1 \le d_1 \le 9$ (since it is a 4-digit number, the first digit cannot be 0)
3. $0 \le d_2, d_3, d_4 \le 9$

First, let $x_1 = d_1 - 1$. Then $0 \le x_1 \le 8$.
The equation becomes:
$(x_1 + 1) + d_2 + d_3 + d_4 = 10$
$x_1 + d_2 + d_3 + d_4 = 9$

Now we need to find the number of non-negative integer solutions to $x_1 + d_2 + d_3 + d_4 = 9$.
Using the stars and bars formula $\binom{n+k-1}{k-1}$, where $n=9$ and $k=4$:
$\binom{9+4-1}{4-1} = \binom{12}{3}$

Calculate $\binom{12}{3}$:
$\binom{12}{3} = \frac{12 \times 11 \times 10}{3 \times 2 \times 1} = 2 \times 11 \times 10 = 220$

Next, we must check if any solutions violate the upper bound constraints ($x_1 \le 8$ and $d_i \le 9$).
The constraint $d_2, d_3, d_4 \le 9$ is automatically satisfied because the sum is only 9.
The only constraint that could be violated is $x_1 \le 8$.
If $x_1 > 8$, then $x_1$ must be at least 9.
If $x_1 = 9$, then $d_2 + d_3 + d_4 = 0$, which means $d_2=0, d_3=0, d_4=0$.
This gives exactly one solution: $(x_1, d_2, d_3, d_4) = (9, 0, 0, 0)$, which corresponds to $(d_1, d_2, d_3, d_4) = (10, 0, 0, 0)$.
However, $d_1$ must be a single digit ($\le 9$), so $d_1=10$ is invalid.

Subtract this one invalid case from the total:
$220 - 1 = 219$

ANSWER: 219