To find the number of integers from 1 to 1000 that are divisible by 3 or 5, but not by 15, we can use set theory and the principle of inclusion-exclusion.

**Step 1: Count the integers divisible by 3.**
To find the number of multiples of 3 in the range 1 to 1000, we divide 1000 by 3 and take the integer part (floor):
$$ \lfloor \frac{1000}{3} \rfloor = 333 $$
There are 333 integers divisible by 3.

**Step 2: Count the integers divisible by 5.**
Similarly, we divide 1000 by 5:
$$ \lfloor \frac{1000}{5} \rfloor = 200 $$
There are 200 integers divisible by 5.

**Step 3: Count the integers divisible by 15.**
An integer is divisible by both 3 and 5 if and only if it is divisible by their least common multiple, which is 15. We divide 1000 by 15:
$$ \lfloor \frac{1000}{15} \rfloor = 66 $$
There are 66 integers divisible by 15.

**Step 4: Analyze the conditions.**
The problem asks for numbers divisible by 3 **OR** 5, but **NOT** by 15.
*   The set of numbers divisible by 3 or 5 is the union of the two sets calculated in Steps 1 and 2.
*   However, simply adding the counts from Step 1 and Step 2 ($333 + 200$) counts the numbers divisible by 15 twice (once in the count for 3, and once in the count for 5).
*   Furthermore, the problem explicitly excludes numbers divisible by 15.

We can solve this by finding the count of numbers divisible by 3 (excluding those divisible by 15) and adding it to the count of numbers divisible by 5 (excluding those divisible by 15).

**Step 5: Calculate the final count.**
*   **Numbers divisible by 3 but not 15:**
    $333 - 66 = 267$
*   **Numbers divisible by 5 but not 15:**
    $200 - 66 = 134$

Since a number cannot be divisible by 3 (but not 5) and divisible by 5 (but not 3) at the same time, these two groups are disjoint (they do not overlap). We simply add them together:

$$ 267 + 134 = 401 $$

Alternatively, using the formula for the symmetric difference:
$$ (\text{Count}_3 + \text{Count}_5) - 2 \times (\text{Count}_{15}) $$
$$ (333 + 200) - 2(66) $$
$$ 533 - 132 = 401 $$

ANSWER: 401