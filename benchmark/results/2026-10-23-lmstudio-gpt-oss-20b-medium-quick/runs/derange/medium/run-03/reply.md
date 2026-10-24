To count the permutations of \(\{1,2,3,4,5,6\}\) in which no element stays in its original place (a **derangement**), we use the principle of inclusion–exclusion.

---

### Step‑by‑step reasoning

Let \(A_i\) be the set of permutations where element \(i\) is fixed (i.e. \(i\) remains in position \(i\)).  
We want the number of permutations that avoid all these events:
\[
N = 6! - \bigl|A_1\cup A_2\cup\dots\cup A_6\bigr|.
\]

The inclusion–exclusion principle tells us
\[
\bigl|\!\bigcup_{i=1}^{6} A_i\bigr|
   = \sum_{k=1}^{6} (-1)^{\,k+1}\!\!\sum_{\substack{S\subseteq\{1,\dots,6\}\\|S|=k}}\! |A_S|,
\]
where \(A_S=\bigcap_{i\in S}A_i\).  
If a particular set \(S\) of size \(k\) is fixed, the remaining \(6-k\) elements can be permuted arbitrarily. Hence
\[
|A_S|=(6-k)! .
\]

There are \(\binom{6}{k}\) different subsets \(S\) of size \(k\).  
Therefore

\[
N = 6! - \sum_{k=1}^{6} (-1)^{\,k+1}\binom{6}{k}(6-k)! .
\]

Rewrite the sum by factoring out \(6!\):
\[
N
   = 6!\left[1-\frac{\binom{6}{1}}{1!}
            +\frac{\binom{6}{2}}{2!}
            -\frac{\binom{6}{3}}{3!}
            +\frac{\binom{6}{4}}{4!}
            -\frac{\binom{6}{5}}{5!}
            +\frac{\binom{6}{6}}{6!}\right].
\]

Compute the alternating sum inside brackets:

\[
\begin{aligned}
1 &- 1
+ \tfrac12 
- \tfrac16 
+ \tfrac1{24} 
- \tfrac1{120} 
+ \tfrac1{720}\\[2mm]
&= \frac{265}{720}.
\end{aligned}
\]

Finally multiply by \(6! = 720\):

\[
N = 720 \times \frac{265}{720}=265.
\]

---

### Result

There are **265** permutations of the six numbers in which no number remains in its original position.

ANSWER: 265