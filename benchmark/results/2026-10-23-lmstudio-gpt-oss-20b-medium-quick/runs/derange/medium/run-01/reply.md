To find how many permutations of the set \(\{1,2,3,4,5,6\}\) have no element in its original position (a *derangement*), we use inclusion–exclusion.

Let  

\[
A_i=\{\text{permutations where }i\text{ is fixed}\}, \qquad i=1,\dots ,6 .
\]

We need the number of permutations that are **not** in any \(A_i\):

\[
N = 6!-\bigl|A_1\cup A_2\cup\dots\cup A_6\bigr|.
\]

By inclusion–exclusion,

\[
|A_1\cup \dots\cup A_6|
   = \sum_{k=1}^{6}(-1)^{\,k-1}\!\!\binom{6}{k}(6-k)! .
\]

Hence

\[
N
  = \sum_{k=0}^{6} (-1)^k \binom{6}{k}(6-k)!
  = 6! - \binom{6}{1}5! + \binom{6}{2}4!
    - \binom{6}{3}3! + \binom{6}{4}2!
    - \binom{6}{5}1! + \binom{6}{6}0!.
\]

Compute each term:

| \(k\) | \((-1)^k\binom{6}{k}(6-k)!\) |
|-------|------------------------------|
| 0 | \(+720\) |
| 1 | \(-6\times120 = -720\) |
| 2 | \(+15\times24 = +360\) |
| 3 | \(-20\times6 = -120\) |
| 4 | \(+15\times2 = +30\) |
| 5 | \(-6\times1 = -6\) |
| 6 | \(+1\times1 = +1\) |

Adding them:

\[
720-720+360-120+30-6+1 = 265 .
\]

Thus there are **265** permutations of the numbers \(1,2,3,4,5,6\) in which no number occupies its original position.

ANSWER: 265