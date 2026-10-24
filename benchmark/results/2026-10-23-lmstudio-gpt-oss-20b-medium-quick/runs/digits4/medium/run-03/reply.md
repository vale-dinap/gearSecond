Let the four digits be \(a,b,c,d\) with  

- \(a \in \{1,2,\dots ,9\}\) (the first digit cannot be zero),  
- \(b,c,d \in \{0,1,\dots ,9\}\).  

We need

\[
a+b+c+d = 10 .
\]

---

### Shift the first digit

Set \(x=a-1\).  
Then \(x\ge 0\) and \(x\le 8\), and the equation becomes

\[
x + b + c + d = 9 .
\]

Now all variables are non‑negative integers. Because their sum is only \(9\),
none of them can exceed \(9\); thus the only upper bound that matters is
\(x \le 8\).

---

### Count unrestricted solutions

The number of non‑negative integer solutions to  

\[
x+b+c+d = 9
\]

is given by stars and bars:

\[
\binom{9+4-1}{4-1}=\binom{12}{3}=220 .
\]

---

### Exclude the forbidden case

The restriction \(x \le 8\) removes the single solution where \(x=9\),
which would correspond to \(a = x+1 = 10\), not a valid digit.  
Thus we subtract one:

\[
220-1 = 219 .
\]

---

Therefore, there are **219** four‑digit positive integers whose digits sum to 10.

ANSWER: 219