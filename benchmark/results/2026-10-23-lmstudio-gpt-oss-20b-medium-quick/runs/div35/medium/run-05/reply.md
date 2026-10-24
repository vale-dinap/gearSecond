We need the number of integers \(n\) with  

- \(1 \le n \le 1000\),
- \(3 \mid n\) or \(5 \mid n\), and  
- \(15 \nmid n\).

Let  

- \(A =\{n: 3\mid n\}\),
- \(B =\{n: 5\mid n\}\),
- \(C =\{n: 15\mid n\}\) (the intersection of \(A\) and \(B\)).

Using inclusion–exclusion:

\[
|A \cup B| = |A| + |B| - |C|.
\]

We want all numbers in \(A \cup B\) that are **not** in \(C\), so

\[
\text{Desired count} = |A \cup B| - |C|
                      = (|A|+|B|-|C|)-|C|
                      = |A| + |B| - 2|C|.
\]

Now compute each cardinality up to \(1000\):

- Multiples of \(3\): \(\left\lfloor \frac{1000}{3}\right\rfloor = 333\).
- Multiples of \(5\): \(\left\lfloor \frac{1000}{5}\right\rfloor = 200\).
- Multiples of \(15\) (both \(3\) and \(5\)): \(\left\lfloor \frac{1000}{15}\right\rfloor = 66\).

Plugging in:

\[
333 + 200 - 2(66) = 533 - 132 = 401.
\]

Thus, **401** integers from 1 to 1000 are divisible by 3 or by 5 but not by 15.

ANSWER: 401