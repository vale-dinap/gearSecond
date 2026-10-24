The problem asks for the number of sequences of moves that sum to 12, where each move is either 1 or 2 steps.  
Let \(k\) be the number of 2‑step moves used. Then:

* The remaining steps are \(12-2k\), all taken as 1‑step moves.
* Total moves made = \(k + (12-2k) = 12-k\).

To form a particular sequence we must choose which of the \(12-k\) move positions contain the \(k\) two‑steps.  
Number of sequences for a fixed \(k\):

\[
\binom{12-k}{\,k\,}.
\]

The possible values of \(k\) are \(0,1,\dots,6\). Sum these binomial coefficients:

\[
\begin{aligned}
k=0:&\ \binom{12}{0}=1\\
k=1:&\ \binom{11}{1}=11\\
k=2:&\ \binom{10}{2}=45\\
k=3:&\ \binom{9}{3}=84\\
k=4:&\ \binom{8}{4}=70\\
k=5:&\ \binom{7}{5}=21\\
k=6:&\ \binom{6}{6}=1
\end{aligned}
\]

Adding them: \(1+11+45+84+70+21+1 = 233\).

Thus there are **233** different ways to climb a staircase of 12 steps using only 1‑step or 2‑step moves.

ANSWER: 233