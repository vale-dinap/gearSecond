To find the number of integers from 1 to 1000 that are divisible by 3 or 5, but not by 15, we can use the principle of inclusion-exclusion.

1. **Find the number of integers divisible by 3:**
   $1000 \div 3 = 333.33...$
   So, there are **333** integers.

2. **Find the number of integers divisible by 5:**
   $1000 \div 5 = 200$
   So, there are **200** integers.

3. **Find the number of integers divisible by both 3 and 5 (i.e., divisible by 15):**
   $1000 \div 15 = 66.66...$
   So, there are **66** integers.

4. **Calculate the number of integers divisible by 3 or 5:**
   Using the formula $|A \cup B| = |A| + |B| - |A \cap B|$:
   $333 + 200 - 66 = 467$

5. **Exclude the integers divisible by 15:**
   The question asks for integers divisible by 3 or 5, **but not by 15**. 
   Since the 467 integers calculated above include one instance of the integers divisible by 15, we must subtract those 66 integers.
   $467 - 66 = 401$

Alternatively, you can think of it as:
(Integers divisible by 3 but not 15) + (Integers divisible by 5 but not 15)
$(333 - 66) + (200 - 66) = 267 + 134 = 401$

ANSWER: 401