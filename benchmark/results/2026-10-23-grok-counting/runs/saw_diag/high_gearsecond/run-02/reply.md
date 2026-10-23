The possible endpoints of an 8-step walk that lie on the line \(y = x\) are the points \((k, k)\) for \(k = 0, \pm 1, \pm 2, \pm 3, \pm 4\). A walk ending at the origin necessarily revisits the origin, so it is not self-avoiding. Thus it is enough to count the self-avoiding walks that terminate at each of the remaining eight points.

Write \(e, w, n, s\) for the number of steps of each type. The conditions \(e - w = n - s = k\) and \(e + w + n + s = 8\) force
\[
w + s = 4 - k
\]
(with \(w, s \ge 0\)). Each admissible pair \((w, s)\) determines a unique step multiset. For every such multiset the self-avoiding realisations are counted by decomposing a walk into horizontal runs separated by its vertical steps (or the symmetric decomposition). Because a run lies on a straight line, it is self-avoiding if and only if it is monotone; when two runs lie on the same horizontal line their intervals of \(x\)-coordinates must be disjoint. The resulting elementary enumerations are:

- \(k = 4\): \(\binom{8}{4} = 70\) walks (only east and north);
- \(k = 3\): \(120\) walks;
- \(k = 2\): \(112\) walks;
- \(k = 1\): \(76\) walks.

(The same figures are obtained for the four negative endpoints by the symmetries of the square lattice.) Adding these contributions yields
\[
2(70 + 120 + 112 + 76) = 756.
\]

ANSWER: 756