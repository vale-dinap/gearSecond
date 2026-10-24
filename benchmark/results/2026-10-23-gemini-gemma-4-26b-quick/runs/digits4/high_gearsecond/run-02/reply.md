To find the number of 4-digit positive integers whose digits sum to 10, we let the digits be $d_1, d_2, d_3,$ and $d_4$.

The conditions are:
1. $d_1 + d_2 + d_3 + d_4 = 10$
2. $1 \le d_1 \le 9$
3. $0 \le d_2 \le 9$
4. $0 \le d_3 \le 9$
5. $0 \le d_4 \le 9$

Let $x_1 = d_1 - 1$. Substituting this into the first equation gives:
$(x_1 + 1) + d_2 + d_3 + d_4 = 10$
$x_1 + d_2 + d_3 + d_4 = 9$

Now the constraints are:
$0 \le x_1 \le 8$
$0 \le d_2 \le 9$
$0 \le d_3 \le 9$
$0 \le d_4 \le 9$

We first calculate the total number of non-negative integer solutions to $x_1 + d_2 + d_3 + d_4 = 9$ using the stars and bars formula, $\binom{n+k-1}{k-1}$, where $n=9$ and $k=4$:
$\binom{9+4-1}{4-1} = \binom{12}{3} = \frac{12 \times 11 \times 10}{3 \times 2 \times 1} = 220$

Next, we check if any solutions violate our constraints.
The constraints for $d_2, d_3,$ and $d_4$ are that they must be $\le 9$. Since the total sum is 9, it is impossible for any of these variables to exceed 9.

The only constraint that could be violated is $x_1 \le 8$. 
If $x_1 > 8$, the only possible integer solution for $x_1 + d_2 + d_3 + d_4 = 9$ is $x_1 = 9$ and $d_2 = d_3 = d_4 = 0$.
This single case $(x_1=9, d_2=0, d_3=0, d_4=0)$ corresponds to $d_1=10$, which is not a single digit.

Subtracting this one invalid case from the total:
$220 - 1 = 219$

ANSWER: 219