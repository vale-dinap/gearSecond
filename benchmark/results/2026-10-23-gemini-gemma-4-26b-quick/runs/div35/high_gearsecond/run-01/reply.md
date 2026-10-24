To find the number of integers from 1 to 1000 that are divisible by 3 or 5, but not by 15, we can use the principle of inclusion-exclusion for sets.

1.  **Find the number of integers divisible by 3:**
    $\lfloor 1000 / 3 \rfloor = 333$

2.  **Find the number of integers divisible by 5:**
    $\lfloor 1000 / 5 \rfloor = 200$

3.  **Find the number of integers divisible by both 3 and 5 (which are the integers divisible by 15):**
    $\lfloor 1000 / 15 \rfloor = 66$

4.  **Calculate the number of integers divisible by 3 or 5:**
    Using the formula $|A \cup B| = |A| + |B| - |A \cap B|$:
    $333 + 200 - 66 = 467$

5.  **Subtract the integers divisible by 15 to satisfy the "but not by 15" condition:**
    The set of integers divisible by 15 is the intersection of the two sets. To remove them from the union, we subtract the intersection once more:
    $467 - 66 = 401$

Alternatively, you can think of it as:
(Integers divisible by 3 only) + (Integers divisible by 5 only)
$(333 - 66) + (200 - 66) = 267 + 134 = 401$

ANSWER: 401