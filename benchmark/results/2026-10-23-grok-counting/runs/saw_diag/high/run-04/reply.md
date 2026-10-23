The 8-step self-avoiding walks that terminate on the diagonal \(y = x\) are precisely the walks that terminate at one of the points \((m, m)\) for \(m = -4, \dots, 4\). The case \(m = 0\) is impossible: the endpoint would coincide with the origin, violating self-avoidance. Symmetry under a \(180^\circ\) rotation shows that the number of walks ending at \((m, m)\) equals the number ending at \((-m, -m)\), so it is enough to treat \(m > 0\) and double.

Each admissible endpoint is analysed by the possible step-multisets (the non-negative integer solutions of \(E - W = m\), \(N - S = m\) and \(E + W + N + S = 8\)). For every multiset the walks are decomposed into vertical sojourns separated by the horizontal steps. A sojourn on the line is self-avoiding if and only if it is monotone, and sojourns that revisit the same vertical line are self-avoiding if and only if their \(y\)-intervals are disjoint. Enumerating the admissible distributions of the north and south steps among these sojourns yields:

- 70 walks to \((4, 4)\) (and likewise to \((-4, -4)\)),
- 120 walks to \((3, 3)\) (and likewise to \((-3, -3)\)),
- 112 walks to \((2, 2)\) (and likewise to \((-2, -2)\)),
- 76 walks to \((1, 1)\) (and likewise to \((-1, -1)\)).

Adding these contributions produces the total.

ANSWER: 756