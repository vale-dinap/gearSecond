To find the number of integers from 1 to 1000 that are divisible by 3 or by 5, but not by 15, we can use the Principle of Inclusion-Exclusion and set logic.

**Step 1: Count the multiples of 3, 5, and 15 in the range [1, 1000].**

The number of multiples of an integer $k$ in the range $[1, n]$ is given by $\lfloor \frac{n}{k} \rfloor$.

*   **Multiples of 3:**
    $\lfloor \frac{1000}{3} \rfloor = 333$
    There are 333 integers divisible by 3.

*   **Multiples of 5:**
    $\lfloor \frac{1000}{5} \rfloor = 200$
    There are 200 integers divisible by 5.

*   **Multiples of 15:**
    $\lfloor \frac{1000}{15} \rfloor = 66$
    There are 66 integers divisible by 15.

**Step 2: Determine the count of integers divisible by 3 or 5.**

The set of integers divisible by 3 or 5 is the union of the set of multiples of 3 and the set of multiples of 5. According to the Principle of Inclusion-Exclusion, the size of the union is the sum of the sizes of the individual sets minus the size of their intersection.

The intersection of "divisible by 3" and "divisible by 5" is the set of numbers divisible by both 3 and 5. Since 3 and 5 are prime, a number is divisible by both if and only if it is divisible by their product, 15.

*   Count (Divisible by 3 or 5) = (Count of Multiples of 3) + (Count of Multiples of 5) - (Count of Multiples of 15)
*   Count (Divisible by 3 or 5) = $333 + 200 - 66$
*   Count (Divisible by 3 or 5) = $533 - 66 = 467$

So, there are 467 integers between 1 and 1000 that are divisible by 3 or 5.

**Step 3: Apply the condition "but not by 15".**

The problem asks us to exclude any integers that are divisible by 15. Since every integer divisible by 15 is already included in our count of 467 (because it is divisible by both 3 and 5), we simply subtract the count of multiples of 15 from the total found in Step 2.

*   Final Count = (Count Divisible by 3 or 5) - (Count Divisible by 15)
*   Final Count = $467 - 66$
*   Final Count = $401$

**Alternative Reasoning (Symmetric Difference):**
We are looking for numbers divisible by 3 but not 5, plus numbers divisible by 5 but not 3.
1.  Multiples of 3 that are not multiples of 5: $333 - 66 = 267$.
2.  Multiples of 5 that are not multiples of 3: $200 - 66 = 134$.
3.  Total = $267 + 134 = 401$.

ANSWER: 401