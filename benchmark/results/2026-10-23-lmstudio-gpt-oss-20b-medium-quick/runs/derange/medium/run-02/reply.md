To count the permutations of \(\{1,2,3,4,5,6\}\) in which no element stays in its original position (a **derangement**), we use the inclusion–exclusion principle.

---

### 1.  Set up

Let  

- \(S\) be all \(6!\) permutations of the six numbers.
- For each \(i=1,\dots ,6\) let \(A_i\) be the set of permutations in which element \(i\) is fixed (i.e., it remains in its original position).

We need \(|S\setminus(A_1\cup A_2\cup\dots \cup A_6)|\), the number of permutations that avoid all events \(A_i\).

---

### 2. Inclusion–Exclusion

The principle states  

\[
|S\setminus\bigcup_{i=1}^6 A_i|
   = \sum_{k=0}^{6}(-1)^k
      \!\!\sum_{\substack{I\subseteq\{1,\dots ,6\\ |I|=k}}
          |\,\cap_{i\in I}A_i|.
\]

If \(k\) particular positions are fixed, the remaining \(6-k\) elements can be permuted arbitrarily: \((6-k)!\) possibilities.  
There are \(\binom{6}{k}\) ways to choose which \(k\) positions are fixed.

Hence

\[
N = \sum_{k=0}^{6}(-1)^k \binom{6}{k}(6-k)! .
\]

---

### 3. Compute the sum

| \(k\) | \((-1)^k\) | \(\displaystyle\binom{6}{k}\) | \((6-k)!\) | Contribution |
|------|-----------|------------------------------|------------|---------------|
|0| + | 1 | \(720\) | \(+720\) |
|1| – | 6 | \(120\) | \(-720\) |
|2| + | 15| \(24\)  | \(+360\) |
|3| – | 20| \(6\)   | \(-120\) |
|4| + | 15| \(2\)   | \(+30\) |
|5| – | 6 | \(1\)    | \(-6\) |
|6| + | 1 | \(1\)    | \(+1\) |

Adding these contributions:

\[
720-720+360-120+30-6+1 = 265 .
\]

---

### 4. Result

There are **265** permutations of the numbers \(1,2,3,4,5,6\) in which no number occupies its original position.

ANSWER: 265