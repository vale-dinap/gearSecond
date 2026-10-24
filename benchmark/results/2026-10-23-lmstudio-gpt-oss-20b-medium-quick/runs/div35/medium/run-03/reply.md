To find how many integers between 1 and 1000 are divisible by 3 or by 5 but **not** by 15, we can use simple counting and the principle of inclusion–exclusion.

---

### 1. Count multiples of each relevant number

- Multiples of \(3\) up to \(1000\):

  \[
  a = \left\lfloor \frac{1000}{3} \right\rfloor = 333
  \]

- Multiples of \(5\) up to \(1000\):

  \[
  b = \left\lfloor \frac{1000}{5} \right\rfloor = 200
  \]

- Multiples of \(15\) (the least common multiple of \(3\) and \(5\)) up to \(1000\):

  \[
  c = \left\lfloor \frac{1000}{15} \right\rfloor = 66
  \]

---

### 2. Use inclusion–exclusion

The set we want is “divisible by 3 or 5” **minus** the numbers that are divisible by 15 (since those are excluded).

- Number of integers divisible by \(3\) or \(5\):

  \[
  |A\cup B| = a + b - c
  \]

  (subtracting \(c\) because multiples of both 3 and 5 were counted twice).

- Subtract the multiples of 15 that we must exclude:

  \[
  \text{Desired count} = |A\cup B| - c = (a+b-c)-c = a + b - 2c
  \]

Plugging in \(a, b, c\):

\[
\begin{aligned}
\text{Count} &= 333 + 200 - 2(66) \\
             &= 533 - 132 \\
             &= 401 .
\end{aligned}
\]

---

### 3. Result

There are **401** integers between 1 and 1000 that are divisible by 3 or by 5 but not by 15.

ANSWER: 401