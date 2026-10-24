To find the number of permutations of \(\{1,2,3,4,5,6\}\) in which no element stays in its original position, we need the derangement count for \(n=6\).

The subfactorial (derangement) formula is  

\[
!n = n!\sum_{k=0}^{n} \frac{(-1)^k}{k!}.
\]

For \(n=6\):

\[
6! = 720
\]

Compute the alternating sum:

\[
\begin{aligned}
S &= \sum_{k=0}^{6}\frac{(-1)^k}{k!}\\[2pt]
&= 1 - 1 + \frac12 - \frac16 + \frac1{24} - \frac1{120} + \frac1{720}.
\end{aligned}
\]

Convert each term to a common denominator of \(720\):

\[
S = \frac{720}{720} - \frac{720}{720} + \frac{360}{720} - \frac{120}{720}
    + \frac{30}{720} - \frac{6}{720} + \frac{1}{720}
  = \frac{265}{720}.
\]

Thus

\[
!6 = 720 \times \frac{265}{720} = 265.
\]

So there are **265** permutations where no number appears in its original position.

ANSWER: 265