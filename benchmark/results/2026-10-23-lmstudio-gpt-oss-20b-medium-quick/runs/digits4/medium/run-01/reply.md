Let the four digits be \(a,b,c,d\).

*   The first digit \(a\) can be \(1,2,\dots ,9\) (it cannot be zero).
*   The other three digits \(b,c,d\) can each be \(0,1,\dots ,9\).
*   We need  
    \[
    a+b+c+d = 10 .
    \]

---

### Convert to non‑negative variables

Set  

\[
a' = a-1 \quad (\text{so } a'=0,1,\dots ,8).
\]

Then the equation becomes  

\[
a'+b+c+d = 9 ,
\]
with all four variables \(a',b,c,d\) being non‑negative integers.

Because the total sum is only \(9\), no variable can exceed \(9\).  
The only possible violation of a digit limit is if \(a'=9\) (which would mean
\(a=10\)), but this cannot happen because \(a'\le 8\).

---

### Count all non‑negative solutions

The number of non‑negative integer solutions to  

\[
x_1+x_2+x_3+x_4 = 9
\]

is given by the stars‑and‑bars formula:

\[
\binom{9+4-1}{4-1}=\binom{12}{3}=220 .
\]

---

### Exclude the impossible case

The only disallowed solution is \(a'=9,\;b=c=d=0\) (which would give
\(a=10\)).  
Thus we subtract one:

\[
220 - 1 = 219 .
\]

No other variable can exceed its digit limit because the total sum is only \(9\).

---

Therefore, there are **219** four‑digit positive integers whose digits sum to \(10\).

ANSWER: 219