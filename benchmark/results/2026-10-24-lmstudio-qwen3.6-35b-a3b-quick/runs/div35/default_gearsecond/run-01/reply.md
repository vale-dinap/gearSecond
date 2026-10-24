Let $A$ be the set of integers in $\{1, \dots, 1000\}$ divisible by 3.
Let $B$ be the set of integers in $\{1, \dots, 1000\}$ divisible by 5.
Let $C$ be the set of integers in $\{1, \dots, 1000\}$ divisible by 15.

We want to find the number of elements in $(A \cup B) \setminus C$.
Since 15 is the least common multiple of 3 and 5, $C = A \cap B$.
Thus, we want $|(A \cup B) \setminus (A \cap B)|$, which is the size of the symmetric difference $|A| + |B| - 2|A \cap B|$.

1.  **Count $|A|$ (multiples of 3):**
    $|A| = \lfloor \frac{1000}{3} \rfloor = 333$.

2.  **Count $|B|$ (multiples of 5):**
    $|B| = \lfloor \frac{1000}{5} \rfloor = 200$.

3.  **Count $|A \cap B|$ (multiples of 15):**
    $|A \cap B| = \lfloor \frac{1000}{15} \rfloor = 66$.

4.  **Calculate the result:**
    Count $= 333 + 200 - 2(66)$
    Count $= 533 - 132$
    Count $= 401$.

ANSWER: 401