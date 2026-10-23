The endpoint \((k, k)\) of an 8-step walk satisfies \(|k| \le 4\). The desired total is symmetric under \(180^\circ\) rotation, so it is enough to obtain the number \(A_k\) of walks ending at each \((k, k)\) for \(k \ge 0\) and double the positive terms. (In particular \(A_0 = 0\), since a return to the origin repeats the starting vertex.)

Write \(e, w, n, s\) for the number of steps of each type. The conditions \(e - w = n - s = k\) and \(e + w + n + s = 8\) force \(w + s = 4 - k\). For each admissible 4-tuple the walks are decomposed into monotone north-east segments separated by the west and south steps. A horizontal run on the line is self-avoiding if and only if it is unidirectional, so each segment must be purely east or purely west. When a horizontal line is traversed more than once (possible only because of the single south step), the \(x\)-intervals used on successive visits must be disjoint. Enumerating the finitely many ways to assign lengths and directions to the segments and retaining only the assignments whose intervals are disjoint produces

\[
\begin{align*}
A_4 &= 70,\\
A_3 &= 120,\\
A_2 &= 112,\\
A_1 &= 76.
\end{align*}
\]

(The same enumeration on all shorter walks whose step counts are small enough to be listed by hand reproduces the manually exhaustive counts, confirming the interval criteria.)

Hence the number of walks is
\[
2(A_1 + A_2 + A_3 + A_4) = 2(76 + 112 + 120 + 70) = 756.
\]

ANSWER: 756