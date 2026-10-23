The possible endpoints on the line \(y = x\) are the lattice points \((k, k)\) for integers \(k\) with \(|k| \le 4\). A self-avoiding walk cannot return to the origin, so there are no such walks ending at \((0, 0)\). Rotation by \(180^\circ\) is a bijection on the self-avoiding walks and swaps \((k, k)\) with \((-k, -k)\), so it is enough to treat \(k > 0\) and double.

Write \(e, w, n, s\) for the number of east, west, north and south steps. Ending at \((k, k)\) forces
\[
w + s = 4 - k, \qquad e = w + k, \qquad n = s + k.
\]
The walks for each pair \((w, s)\) are counted by separating the walk into unidirectional straight sojourns (any reversal on a line immediately repeats a vertex) and requiring that sojourns that return to the same horizontal or vertical line occupy disjoint intervals of sites.

- For \(k = 4\) one has \(w = s = 0\). Every word of four E’s and four N’s is self-avoiding, so there are \(\binom{8}{4} = 70\) walks.
- For \(k = 3\) the two pairs \((w, s)\) are \((1, 0)\) and \((0, 1)\). In the first case the single west step must occupy a horizontal level by itself and the four east steps are distributed on the remaining levels, giving \(4 \times 15 = 60\) walks; reflection across \(y = x\) supplies another 60. Total: \(120\).
- For \(k = 2\) the pairs are \((2, 0)\), \((0, 2)\) and \((1, 1)\). The first gives 18 walks (the two west steps lie on one level, or on two distinct levels). The second likewise gives 18. For one west and one south the four possible orders of the vertical steps, together with the admissible placements of the west step among the gaps, produce \(32 + 6 + 6 + 32 = 76\) walks. Total: \(112\).
- For \(k = 1\) the pairs are \((3, 0)\), \((0, 3)\), \((1, 2)\) and \((2, 1)\). With no west step the single east step separates a pure north sojourn from a pure south sojourn, giving exactly two walks; the symmetric pair likewise gives two. For one west and two south steps the three possible orders of the horizontal steps produce \(18 + 0 + 18 = 36\) walks, and the remaining pair contributes another 36. Total: \(76\).

Adding these contributions and doubling for the negative diagonal yields
\[
2 \times (70 + 120 + 112 + 76) = 756.
\]

ANSWER: 756