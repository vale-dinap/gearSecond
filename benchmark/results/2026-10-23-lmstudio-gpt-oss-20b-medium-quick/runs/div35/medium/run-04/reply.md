To find the integers between \(1\) and \(1000\) that are divisible by \(3\) or \(5\) but **not** by \(15\), we can use basic counting principles.

Let  

- \(A\) = set of numbers divisible by \(3\).  
- \(B\) = set of numbers divisible by \(5\).  
- \(C\) = set of numbers divisible by both \(3\) and \(5\); since the least common multiple of \(3\) and \(5\) is \(15\), \(C\) is precisely the set of multiples of \(15\).

We want all numbers that are in \(A \cup B\) **except** those in \(C\).  
That is, we need

\[
| (A \cup B) \setminus C | = |A| + |B| - 2|C|.
\]

Now count each set up to \(1000\):

1. Multiples of \(3\): \(\left\lfloor \dfrac{1000}{3} \right\rfloor = 333.\)

2. Multiples of \(5\): \(\left\lfloor \dfrac{1000}{5} \right\rfloor = 200.\)

3. Multiples of \(15\) (both \(3\) and \(5\)): \(\left\lfloor \dfrac{1000}{15} \right\rfloor = 66.\)

Plugging these into the formula:

\[
|A| + |B| - 2|C| = 333 + 200 - 2(66) = 533 - 132 = 401.
\]

Thus, **401** integers between \(1\) and \(1000\) are divisible by \(3\) or \(5\) but not by \(15\).

ANSWER: 401