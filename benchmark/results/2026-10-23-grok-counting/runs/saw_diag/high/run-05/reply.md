The possible endpoints of an 8-step walk that lie on the line \(y = x\) are the points \((k, k)\) for integers \(k\) with \(|k| \le 4\). A walk of positive length cannot be self-avoiding and finish at the origin, so the contribution of \(k = 0\) is 0. Rotation by \(180^\circ\) is a bijection between the walks ending at \((k, k)\) and those ending at \((-k, -k)\), so it is enough to treat \(k > 0\) and double.

Write \(e, w, n, s\) for the number of steps of each type. The conditions \(e - w = n - s = k\) and \(e + w + n + s = 8\) force \(w + s = 4 - k\). For each admissible pair \((w, s)\) the resulting walks are sequences whose vertical sojourns (the runs of \(\mathrm{N}/\mathrm{S}\) steps lying between consecutive horizontal steps) are strictly monotone; any change of vertical direction inside a sojourn immediately repeats a vertex. When the same vertical line is visited more than once, the \(y\)-intervals occupied on that line must be disjoint. Enumerating the admissible placements of the horizontal steps and the monotone sojourns yields:

- \(k = 4\): only \(4\mathrm{E}+4\mathrm{N}\), and every such sequence is self-avoiding, so there are \(\binom{8}{4} = 70\) walks;
- \(k = 3\): \(60\) walks of type \(3\mathrm{E}+4\mathrm{N}+1\mathrm{S}\) and \(60\) of type \(4\mathrm{E}+1\mathrm{W}+3\mathrm{N}\), hence \(120\) walks;
- \(k = 2\): \(18\) walks of type \(2\mathrm{E}+4\mathrm{N}+2\mathrm{S}\), \(18\) of type \(4\mathrm{E}+2\mathrm{W}+2\mathrm{N}\), and \(76\) of type \(3\mathrm{E}+1\mathrm{W}+3\mathrm{N}+1\mathrm{S}\), hence \(112\) walks;
- \(k = 1\): \(2\) walks of type \(1\mathrm{E}+4\mathrm{N}+3\mathrm{S}\), \(2\) of type \(4\mathrm{E}+3\mathrm{W}+1\mathrm{N}\), and \(36\) walks in each of the two mixed types with \(w + s = 3\), hence \(76\) walks.

Doubling for negative \(k\) therefore produces
\[
2(70 + 120 + 112 + 76) = 756.
\]

ANSWER: 756