To find the number of integers from 1 to 1000 that are divisible by 3 or by 5, but not by 15, we can break the problem down into sets and use the Principle of Inclusion-Exclusion.

**1. Identify the sets of numbers:**
*   Let $A$ be the set of integers from 1 to 1000 divisible by 3.
*   Let $B$ be the set of integers from 1 to 1000 divisible by 5.
*   Let $C$ be the set of integers from 1 to 1000 divisible by 15.

Note that a number is divisible by 15 if and only if it is divisible by both 3 and 5. Therefore, set $C$ is the intersection of sets $A$ and $B$ ($C = A \cap B$).

**2. Calculate the size of each set:**
The number of multiples of an integer $k$ in the range 1 to $N$ is given by $\lfloor \frac{N}{k} \rfloor$. Here $N = 1000$.

*   **Count of $A$ (multiples of 3):**
    $\lfloor \frac{1000}{3} \rfloor = 333$
    (Since $333 \times 3 = 999$)

*   **Count of $B$ (multiples of 5):**
    $\lfloor \frac{1000}{5} \rfloor = 200$
    (Since $200 \times 5 = 1000$)

*   **Count of $C$ (multiples of 15):**
    $\lfloor \frac{1000}{15} \rfloor = 66$
    (Since $66 \times 15 = 990$)

**3. Determine the count of numbers divisible by 3 OR 5:**
We want the size of the union of sets $A$ and $B$ ($|A \cup B|$). According to the Principle of Inclusion-Exclusion:
$$|A \cup B| = |A| + |B| - |A \cap B|$$
$$|A \cup B| = 333 + 200 - 66$$
$$|A \cup B| = 467$$
So, there are 467 integers divisible by 3 or 5.

**4. Apply the condition "but not by 15":**
The problem asks for integers in the set $A \cup B$ that are *not* in set $C$.
Since every multiple of 15 is also a multiple of 3 (and 5), the set $C$ is entirely contained within $A \cup B$. Therefore, we simply subtract the count of multiples of 15 from the count of the union.

$$\text{Result} = |A \cup B| - |C|$$
$$\text{Result} = 467 - 66$$
$$\text{Result} = 401$$

**Alternative Reasoning:**
We can also view this as counting numbers divisible by 3 only (excluding multiples of 5) plus numbers divisible by 5 only (excluding multiples of 3).
*   Numbers divisible by 3 but not 15 (which implies not 5): $333 - 66 = 267$.
*   Numbers divisible by 5 but not 15 (which implies not 3): $200 - 66 = 134$.
*   Total: $267 + 134 = 401$.

ANSWER: 401