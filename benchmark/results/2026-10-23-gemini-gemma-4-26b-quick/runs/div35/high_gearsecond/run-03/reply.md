To find the number of integers from 1 to 1000 that are divisible by 3 or 5, but not by 15, we can use the principle of inclusion-exclusion and the concept of symmetric difference.

1.  **Find the number of integers divisible by 3:**
    $\lfloor 1000 / 3 \rfloor = 333$

2.  **Find the number of integers divisible by 5:**
    $\lfloor 1000 / 5 \rfloor = 200$

3.  **Find the number of integers divisible by both 3 and 5 (i.e., divisible by 15):**
    $\lfloor 1000 / 15 \rfloor = 66$

4.  **Apply the condition:**
    We want the integers that are in the set of multiples of 3 or the set of multiples of 5, but excluding those that are in both. This is the symmetric difference of the two sets.
    The formula is: $(\text{multiples of 3}) + (\text{multiples of 5}) - 2 \times (\text{multiples of 15})$

    Calculation:
    $333 + 200 - 2(66)$
    $533 - 132 = 401$

Alternatively, you can think of it as:
(Multiples of 3 only) + (Multiples of 5 only)
$(333 - 66) + (200 - 66) = 267 + 134 = 401$

ANSWER: 401