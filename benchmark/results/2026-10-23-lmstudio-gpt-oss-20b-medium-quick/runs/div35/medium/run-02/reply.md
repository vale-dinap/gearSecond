To find how many integers between \(1\) and \(1000\) are divisible by \(3\) or by \(5\), but **not** by both (i.e., not by \(15\)), we can use basic counting principles.

---

### 1. Count multiples of each divisor

- **Multiples of 3:**  
  \[
  \left\lfloor \frac{1000}{3} \right\rfloor = 333
  \]

- **Multiples of 5:**  
  \[
  \left\lfloor \frac{1000}{5} \right\rfloor = 200
  \]

### 2. Count multiples that are counted twice (multiples of both 3 and 5)

The numbers divisible by both \(3\) and \(5\) are exactly the multiples of their least common multiple, \(15\).

- **Multiples of 15:**  
  \[
  \left\lfloor \frac{1000}{15} \right\rfloor = 66
  \]

### 3. Apply inclusion–exclusion to get all numbers divisible by 3 or 5

\[
N_{\text{(3 or 5)}} = N_{3} + N_{5} - N_{15}
= 333 + 200 - 66 = 467
\]

This counts every integer that is a multiple of \(3\) **or** \(5\), including those that are multiples of both.

### 4. Exclude the numbers that are divisible by 15

We want *not* to count any number that is also a multiple of \(15\).  
Subtracting the \(66\) such numbers gives:

\[
N_{\text{desired}} = N_{\text{(3 or 5)}} - N_{15}
= 467 - 66 = 401
\]

---

### Alternative viewpoint

Count separately:

- Multiples of \(3\) **but not** \(5\):  
  \(333 - 66 = 267\)

- Multiples of \(5\) **but not** \(3\):  
  \(200 - 66 = 134\)

Sum: \(267 + 134 = 401\).

Both approaches yield the same result.

---

**Answer:**  

ANSWER: 401