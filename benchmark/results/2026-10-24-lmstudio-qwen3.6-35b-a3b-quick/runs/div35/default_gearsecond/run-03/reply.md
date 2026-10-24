Let $A$ be the set of integers from 1 to 1000 divisible by 3.
Let $B$ be the set of integers from 1 to 1000 divisible by 5.
Let $C$ be the set of integers from 1 to 1000 divisible by 15.

We want to find the number of integers in $(A \cup B) \setminus C$.
Since any integer divisible by 15 is divisible by both 3 and 5, $C = A \cap B$.
Also $C \subseteq A \cup B$.
The count is $|A \cup B| - |C|$.
Using inclusion-exclusion, $|A \cup B| = |A| + |B| - |A \cap B| = |A| + |B| - |C|$.
So the result is $|A| + |B| - 2|C|$.

Calculate $|A|$:
$|A| = \lfloor 1000/3 \rfloor = 333$.

Calculate $|B|$:
$|B| = \lfloor 1000/5 \rfloor = 200$.

Calculate $|C|$:
$|C| = \lfloor 1000/15 \rfloor = 66$.

Compute the final count:
$333 + 200 - 2(66)$
$= 533 - 132$
$= 401$.

ANSWER: 401