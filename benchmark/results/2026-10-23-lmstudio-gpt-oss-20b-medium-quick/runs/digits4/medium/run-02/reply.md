To count the four‑digit numbers whose digits add to \(10\), let  

\[
a,b,c,d \quad (1\le a\le 9,\;0\le b,c,d\le 9)
\]

be the thousands, hundreds, tens and units digits.  
We need

\[
a+b+c+d=10 .
\]

---

### Step 1: Fix the first digit \(a\)

For each possible value of \(a\) (from \(1\) to \(9\)), set  

\[
s = 10-a .
\]

Then \(b+c+d=s\), where \(0\le b,c,d\le 9\).  
Because \(s \le 9\), the upper bound \(9\) on each of \(b, c, d\) is automatically satisfied; any non‑negative solution to \(b+c+d=s\) will have each variable at most \(s\le9\).

---

### Step 2: Count solutions for \(b+c+d=s\)

The number of non‑negative integer solutions to  

\[
b+c+d = s
\]

is given by the stars‑and‑bars formula:

\[
\binom{s+3-1}{3-1}=\binom{s+2}{2}.
\]

---

### Step 3: Sum over all admissible \(a\)

Compute \(\binom{s+2}{2}\) for each \(s = 10-a\):

| \(a\) | \(s=10-a\) | \(\displaystyle \binom{s+2}{2}\) |
|------|-----------|----------------------------|
| 1 | 9 | 55 |
| 2 | 8 | 45 |
| 3 | 7 | 36 |
| 4 | 6 | 28 |
| 5 | 5 | 21 |
| 6 | 4 | 15 |
| 7 | 3 | 10 |
| 8 | 2 | 6  |
| 9 | 1 | 3  |

Add them:

\[
55+45+36+28+21+15+10+6+3 = 219.
\]

---

### Result

There are **219** four‑digit positive integers whose digits sum to \(10\).

ANSWER: 219