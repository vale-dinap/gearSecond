The possible endpoints on the line \(y = x\) are the points \((a, a)\) for integers \(a\) with \(|a| \le 4\). The 180° rotational symmetry of the square lattice interchanges the sets of walks ending at \((a, a)\) and at \((-a, -a)\), so it is enough to treat \(a \ge 0\) and double. No positive-length self-avoiding walk can end at the origin, so the contribution of \(a = 0\) is zero.

For each \(a \ge 1\) the admissible step counts \((E, W, N, S)\) are enumerated and the self-avoiding sequences with those counts are counted by cases on the vertical level that contains each south (or west) step. Because a coordinate never decreases until the first step in the opposite direction, every sojourn on a fixed horizontal or vertical line must be monotone; the first reversal on a line immediately repeats a vertex. This reduces the problem to distributing the steps of each direction onto levels and retaining only those distributions for which the unique candidate cells that could coincide are in fact distinct. The resulting counts are:

- \(a = 4\): \(\binom{8}{4} = 70\),
- \(a = 3\): \(120\),
- \(a = 2\): \(112\),
- \(a = 1\): \(76\).

Doubling the positive-\(a\) contributions therefore yields
\[
2(70 + 120 + 112 + 76) = 756.
\]

ANSWER: 756