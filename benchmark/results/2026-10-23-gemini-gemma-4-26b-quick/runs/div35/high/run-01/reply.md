To find the number of integers from 1 to 1000 that are divisible by 3 or by 5, but not by 15, we can use the principle of inclusion-exclusion and set theory.

1.  **Define the sets:**
    *   Let $A$ be the set of integers from 1 to 1000 divisible by 3.
    *   Let $B$ be the set of integers from 1 to 1000 divisible by 5.
    *   The set of integers divisible by both 3 and 5 is the set of integers divisible by $\text{lcm}(3, 5) = 15$. This is represented as $A \cap B$.

2.  **Calculate the number of elements in each set:**
    *   The number of elements in $A$ is $|A| = \lfloor \frac{1000}{3} \rfloor = 333$.
    *   The number of elements in $B$ is $|B| = \lfloor \frac{1000}{5} \rfloor = 200$.
    *   The number of elements in $A \cap B$ is $|A \cap B| = \lfloor \frac{1000}{15} \rfloor$.
        To find $\lfloor \frac{1000}{15} \rfloor$:
        $1000 \div 15 = 66.666...$
        So, $|A \cap B| = 66$.

3.  **Determine the target set:**
    *   The problem asks for integers divisible by 3 or 5, but not by 15. This is the symmetric difference of sets $A$ and $B$, denoted as $A \Delta B$.
    *   The formula for the number of elements in the symmetric difference is:
        $|A \Delta B| = |A \cup B| - |A \cap B|$
    *   We know that $|A \cup B| = |A| + |B| - |A \cap B|$.
    *   Substituting this into the formula, we get:
        $|A \Delta B| = (|A| + |B| - |A \cap B|) - |A \cap B| = |A| + |B| - 2|A \cap B|$

4.  **Perform the final calculation:**
    *   $|A \Delta B| = 333 + 200 - 2(66)$
    *   $|A \Delta B| = 533 - 132$
    *   $|A \Delta B| = 401$

Alternatively, we can calculate the number of elements in $A$ that are not in $B$ and the number of elements in $B$ that are not in $A$:
*   $|A \setminus B| = |A| - |A \cap B| = 333 - 66 = 267$
*   $|B \setminus A| = |B| - |A \cap B| = 200 - 66 = 134$
*   Total = $267 + 134 = 401$

ANSWER: 401