To find the number of integers from 1 to 1000 that are divisible by 3 or by 5, but not by 15, we can use the principle of inclusion-exclusion for sets.

1.  **Identify the sets:**
    *   Let $A$ be the set of integers from 1 to 1000 that are divisible by 3.
    *   Let $B$ be the set of integers from 1 to 1000 that are divisible by 5.
    *   The set of integers divisible by both 3 and 5 is the set of integers divisible by the least common multiple of 3 and 5, which is 15. Thus, $A \cap B$ is the set of integers from 1 to 1000 that are divisible by 15.

2.  **Calculate the number of elements in each set:**
    *   The number of elements in $A$ is $|A| = \lfloor \frac{1000}{3} \rfloor = 333$.
    *   The number of elements in $B$ is $|B| = \lfloor \frac{1000}{5} \rfloor = 200$.
    *   The number of elements in $A \cap B$ is $|A \cap B| = \lfloor \frac{1000}{15} \rfloor = 66$.

3.  **Interpret the question:**
    The question asks for integers divisible by 3 or 5, but not by 15. This is the symmetric difference of sets $A$ and $B$, which is $(A \cup B) \setminus (A \cap B)$.

4.  **Apply the formula for the size of the symmetric difference:**
    The size of the union $|A \cup B|$ is:
    $$|A \cup B| = |A| + |B| - |A \cap B|$$
    $$|A \cup B| = 333 + 200 - 66 = 467$$

    The size of the symmetric difference $|A \Delta B|$ is:
    $$|A \Delta B| = |A \cup B| - |A \cap B|$$
    $$|A \Delta B| = 467 - 66 = 401$$

    Alternatively, using the formula $|A| + |B| - 2|A \cap B|$:
    $$|A \Delta B| = 333 + 200 - 2(66)$$
    $$|A \Delta B| = 533 - 132 = 401$$

5.  **Double-check the steps:**
    *   Multiples of 3 (not 15): $333 - 66 = 267$
    *   Multiples of 5 (not 15): $200 - 66 = 134$
    *   Total: $267 + 134 = 401$

ANSWER: 401