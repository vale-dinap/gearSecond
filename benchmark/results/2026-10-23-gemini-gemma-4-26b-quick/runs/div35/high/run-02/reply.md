To find the number of integers from 1 to 1000 that are divisible by 3 or by 5, but not by 15, we can use the principle of inclusion-exclusion for sets.

1.  **Identify the sets:**
    *   Let $A$ be the set of integers from 1 to 1000 that are divisible by 3.
    *   Let $B$ be the set of integers from 1 to 1000 that are divisible by 5.
    *   An integer is divisible by 15 if and only if it is divisible by both 3 and 5. Thus, the set of integers divisible by 15 is $A \cap B$.

2.  **Calculate the size of each set:**
    *   The number of integers in $A$ is $|A| = \lfloor \frac{1000}{3} \rfloor = 333$.
    *   The number of integers in $B$ is $|B| = \lfloor \frac{1000}{5} \rfloor = 200$.
    *   The number of integers in $A \cap B$ is $|A \cap B| = \lfloor \frac{1000}{15} \rfloor$.
        *   $1000 \div 15 = 66.666...$, so $|A \cap B| = 66$.

3.  **Determine the number of integers divisible by 3 or 5:**
    Using the inclusion-exclusion principle:
    $|A \cup B| = |A| + |B| - |A \cap B|$
    $|A \cup B| = 333 + 200 - 66 = 467$.

4.  **Exclude the integers divisible by 15:**
    The question asks for integers divisible by 3 or 5, but *not* by 15. This is the symmetric difference of sets $A$ and $B$, or $(A \cup B) \setminus (A \cap B)$.
    $| (A \cup B) \setminus (A \cap B) | = |A \cup B| - |A \cap B|$
    $| (A \cup B) \setminus (A \cap B) | = 467 - 66 = 401$.

Alternatively, we can calculate this as:
$|A \setminus B| + |B \setminus A| = (|A| - |A \cap B|) + (|B| - |A \cap B|)$
$= (333 - 66) + (200 - 66)$
$= 267 + 134 = 401$.

ANSWER: 401