To find the four‑digit integers whose digits sum to \(10\), let  

\[
a,b,c,d
\]

be the thousands, hundreds, tens and units digits respectively.  
We need

\[
a+b+c+d=10,\qquad a\in\{1,\dots ,9\},\; b,c,d\in\{0,\dots ,9\}.
\]

---

### 1. Remove the restriction on \(a\)

Set \(a'=a-1\).  
Then \(a'\) ranges from \(0\) to \(8\) and

\[
(a'+1)+b+c+d=10 \;\Longrightarrow\; a'+b+c+d=9.
\]

Now we count non‑negative integer solutions of  

\[
a'+b+c+d=9
\]

with the only restriction that \(a'\le 8\).  
Because the sum is \(9\), no variable can exceed \(9\); thus the bounds for
\(b,c,d\) are automatically satisfied.  
The only potential violation comes from \(a'=9\).

---

### 2. Count all solutions without the upper bound

For a non‑negative equation with four variables, the number of solutions is

\[
\binom{9+4-1}{4-1}=\binom{12}{3}=220.
\]

---

### 3. Exclude the forbidden case \(a'=9\)

If \(a'=9\), then \(b=c=d=0\).  
This single solution corresponds to \(a=10\) (not a valid thousands digit).
Hence we subtract it:

\[
220-1 = 219.
\]

---

### 4. Verify with an alternative sum

For each possible leading digit \(a\) from \(1\) to \(9\),
the remaining three digits must sum to \(s=10-a\) (which is \(\le 9\)).
The number of non‑negative solutions for \(b+c+d=s\) is  

\[
\binom{s+2}{2}.
\]

Summing over all \(a\):

\[
\begin{aligned}
&\binom{11}{2}+ \binom{10}{2}+ \binom{9}{2}+ \binom{8}{2}+ \binom{7}{2}\\
&+\binom{6}{2}+ \binom{5}{2}+ \binom{4}{2}+ \binom{3}{2} = 55+45+36+28+21+15+10+6+3=219.
\end{aligned}
\]

Both methods give the same result.

---

**Answer:** There are **219** four‑digit positive integers whose digits sum to \(10\).

ANSWER: 219