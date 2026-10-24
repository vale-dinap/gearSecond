Let $S = \{1, 2, \dots, 1000\}$.
Let $A$ be the set of integers in $S$ divisible by 3.
Let $B$ be the set of integers in $S$ divisible by 5.
Let $C$ be the set of integers in $S$ divisible by 15.

We want to find the number of integers in $(A \cup B) \setminus C$.
Since a number is divisible by 15 if and only if it is divisible by both 3 and 5, $C = A \cap B$.
The set $(A \cup B) \setminus (A \cap B)$ is the symmetric difference of $A$ and $B$.
The size is given by $|A| + |B| - 2|C|$.

Calculate $|A|$:
$|A| = \lfloor 1000 / 3 \rfloor = 333$.

Calculate $|B|$:
$|B| = \lfloor 1000 / 5 \rfloor = 200$.

Calculate $|C|$:
$|C| = \lfloor 1000 / 15 \rfloor = 66$.

Calculate the result:
$333 + 200 - 2(66)$
$= 533 - 132$
$= 401$.

ANSWER: 401