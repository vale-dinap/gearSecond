To find how many integers from 1 to 1000 are divisible by \(3\) or by \(5\), but **not** by \(15\), we count the multiples of each divisor and then exclude those that are multiples of both.

---

### 1. Count multiples of each divisor

| Divisor | Multiples in \(1 \le n \le 1000\) |
|---------|-----------------------------------|
| \(3\)   | \(\left\lfloor\dfrac{1000}{3}\right\rfloor = 333\) |
| \(5\)   | \(\left\lfloor\dfrac{1000}{5}\right\rfloor = 200\) |

### 2. Count multiples of both (i.e., multiples of the least common multiple)

The lcm of \(3\) and \(5\) is \(15\).

| Divisor | Multiples in \(1 \le n \le 1000\) |
|---------|-----------------------------------|
| \(15\)  | \(\left\lfloor\dfrac{1000}{15}\right\rfloor = 66\) |

These \(66\) numbers are divisible by both \(3\) and \(5\), hence also by \(15\).

---

### 3. Count numbers divisible by **either** \(3\) or \(5\)

Using inclusion–exclusion:

\[
|A \cup B| = |A| + |B| - |A \cap B|
           = 333 + 200 - 66
           = 467 .
\]

So, there are \(467\) integers between \(1\) and \(1000\) that are divisible by \(3\) or by \(5\).

---

### 4. Exclude those divisible by \(15\)

All numbers divisible by \(15\) were already counted in the union above; we need to remove them entirely:

\[
467 - 66 = 401 .
\]

(Equivalently:  
Divisible by \(3\) but **not** \(15\): \(333-66=267\).  
Divisible by \(5\) but **not** \(15\): \(200-66=134\).  
Sum \(267+134 = 401\).)

---

\[
\boxed{401}
\]

ANSWER: 401