Let \(A_i\) be the set of permutations in which the number \(i\) stays fixed (in its original position).  
We want the number of permutations that are **not** in any \(A_i\); i.e., those that have no fixed points.

The total number of permutations of six distinct numbers is  

\[
6! = 720 .
\]

Using the inclusion–exclusion principle we subtract the permutations with at least one fixed point, then add back those counted twice, etc.:

\[
\begin{aligned}
N &= \sum_{k=0}^{6}(-1)^k\binom{6}{k}(6-k)!\\[4pt]
  &= \binom{6}{0}\!6!-\binom{6}{1}\!5!
     +\binom{6}{2}\!4!-\binom{6}{3}\!3!
     +\binom{6}{4}\!2!-\binom{6}{5}\!1!
     +\binom{6}{6}\!0!.
\end{aligned}
\]

Compute each term:

| \(k\) | \(\binom{6}{k}(6-k)!\) | Sign | Value |
|------|------------------------|------|-------|
| 0 | \(1\times720 = 720\) | + | 720 |
| 1 | \(6\times120 = 720\) | – | –720 |
| 2 | \(15\times24 = 360\) | + | 360 |
| 3 | \(20\times6   = 120\) | – | –120 |
| 4 | \(15\times2   = 30\)  | + | 30 |
| 5 | \(6\times1    = 6\)   | – | –6 |
| 6 | \(1\times1    = 1\)   | + | 1 |

Adding them:

\[
720-720+360-120+30-6+1 = 265 .
\]

Thus there are **265** permutations of \(\{1,2,3,4,5,6\}\) in which no number appears in its original position.

(Equivalently, the subfactorial \( !6 = 265 \).)

ANSWER: 265