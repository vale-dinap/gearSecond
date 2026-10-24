Let the four digits be \(d_1,d_2,d_3,d_4\) with  

- \(d_1\in\{1,2,\dots ,9\}\) (the number must be a 4‑digit integer),  
- \(d_i\in\{0,1,\dots ,9\}\) for \(i=2,3,4\).  

We need

\[
d_1+d_2+d_3+d_4 = 10 .
\]

Because the total sum is only \(10\), none of the digits can exceed \(9\); if any digit were \(10\) or more, the remaining digits would have to be negative.  
Hence the only restriction besides non‑negativity is that \(d_1\ge 1\).

---

### Reduce to a standard stars‑and‑bars problem

Let  

\[
y_1 = d_1-1 \quad (\text{so } y_1\ge0).
\]

Then

\[
y_1 + d_2 + d_3 + d_4 = 10-1 = 9 .
\]

Now we are looking for the number of non‑negative integer solutions to  

\[
y_1 + d_2 + d_3 + d_4 = 9,
\]

with no upper bounds needed because each variable is at most \(9\) automatically (the sum itself is only \(9\)).

By stars and bars, the number of such solutions is

\[
\binom{9+4-1}{4-1}=\binom{12}{3}=220 .
\]

Each solution corresponds uniquely to a 4‑digit integer whose digits sum to \(10\).

---

**Answer:**  

\[
\boxed{220}
\]