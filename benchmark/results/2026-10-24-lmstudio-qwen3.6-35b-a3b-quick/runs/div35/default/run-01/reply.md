To find the number of integers from 1 to 1000 that are divisible by 3 or by 5, but not by 15, we can use the Principle of Inclusion-Exclusion and set theory.

**Step 1: Count the integers divisible by 3.**
The number of multiples of 3 in the range 1 to 1000 is found by dividing 1000 by 3 and taking the integer part (floor).
$$ \lfloor \frac{1000}{3} \rfloor = 333 $$
So, there are 333 integers divisible by 3.

**Step 2: Count the integers divisible by 5.**
Similarly, the number of multiples of 5 in the range 1 to 1000 is:
$$ \lfloor \frac{1000}{5} \rfloor = 200 $$
So, there are 200 integers divisible by 5.

**Step 3: Count the integers divisible by both 3 and 5 (i.e., divisible by 15).**
A number is divisible by both 3 and 5 if and only if it is divisible by their least common multiple, which is 15.
$$ \lfloor \frac{1000}{15} \rfloor = 66 $$
So, there are 66 integers divisible by 15.

**Step 4: Calculate the number of integers divisible by 3 OR 5.**
Using the Principle of Inclusion-Exclusion, the count of numbers divisible by 3 or 5 is the sum of the individual counts minus the count of numbers divisible by both (to avoid double counting).
$$ \text{Count}(3 \cup 5) = \text{Count}(3) + \text{Count}(5) - \text{Count}(15) $$
$$ \text{Count}(3 \cup 5) = 333 + 200 - 66 = 467 $$

**Step 5: Exclude integers divisible by 15.**
The problem asks for integers that are divisible by 3 or 5 **but not by 15**.
We have already calculated that there are 467 integers divisible by 3 or 5. Among these 467 integers, the ones divisible by 15 are included. Since every integer divisible by 15 is also divisible by 3 (and by 5), all 66 multiples of 15 are contained within the set of 467 integers.
Therefore, we simply subtract the count of multiples of 15 from the total count of multiples of 3 or 5.

$$ \text{Final Count} = 467 - 66 = 401 $$

Alternatively, you can view this as the sum of:
1.  Integers divisible by 3 but not 5: $333 - 66 = 267$
2.  Integers divisible by 5 but not 3: $200 - 66 = 134$
Total: $267 + 134 = 401$.

ANSWER: 401