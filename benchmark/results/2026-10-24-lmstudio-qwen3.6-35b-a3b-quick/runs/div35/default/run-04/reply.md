To solve this problem, we'll use basic counting principles and the inclusion-exclusion principle.

Let $A$ be the set of integers from 1 to 1000 that are divisible by 3.
Let $B$ be the set of integers from 1 to 1000 that are divisible by 5.

We want to find the number of integers that are in $A \cup B$ (divisible by 3 or 5) but **not** in the set of integers divisible by 15. Note that an integer is divisible by both 3 and 5 if and only if it is divisible by $\text{lcm}(3,5) = 15$. Therefore, the set of multiples of 15 is exactly $A \cap B$.

The quantity we seek is $|(A \cup B) \setminus (A \cap B)|$, which is the size of the symmetric difference of $A$ and $B$.

**Step 1: Count the multiples of 3**
The number of multiples of 3 in the range 1 to 1000 is $\lfloor \frac{1000}{3} \rfloor = 333$.

**Step 2: Count the multiples of 5**
The number of multiples of 5 in the range 1 to 1000 is $\lfloor \frac{1000}{5} \rfloor = 200$.

**Step 3: Count the multiples of 15 (intersection)**
The number of multiples of 15 in the range 1 to 1000 is $\lfloor \frac{1000}{15} \rfloor = 66$.

**Step 4: Apply Inclusion-Exclusion for "divisible by 3 or 5"**
$|A \cup B| = |A| + |B| - |A \cap B| = 333 + 200 - 66 = 467$.
So, there are 467 integers divisible by 3 or 5.

**Step 5: Exclude those divisible by 15**
The problem specifically excludes numbers divisible by 15. Since all multiples of 15 are already counted in the 467 above, we simply subtract them:
$467 - 66 = 401$.

**Alternative Verification:**
We can also count directly by splitting into two disjoint groups:
- Numbers divisible by 3 but not by 5: $333 - 66 = 267$
- Numbers divisible by 5 but not by 3: $200 - 66 = 134$
Adding these disjoint groups gives $267 + 134 = 401$.

Both methods yield the same result.

ANSWER: 401