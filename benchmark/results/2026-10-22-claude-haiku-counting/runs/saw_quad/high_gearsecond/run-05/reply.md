**Answer: 1218**

I worked this by hand without code.

1. **Symmetry decomposition.** The total number of 8-step SAWs from the origin is c₈ = 5916. A walk cannot end at the origin, so every walk ends in an open quadrant or on a half-axis. The dihedral symmetry of the square lattice gives c₈ = 4Q + 4A, where Q is the count ending in the open first quadrant and A is the count ending on the positive x-axis.

2. **Positive x-axis count.** A = N(2,0) + N(4,0) + N(6,0) + N(8,0), with N(2,0) = 92, N(4,0) = 126, N(6,0) = 42, N(8,0) = 1. So A = 261.

3. **Solve.** Q = (5916 − 4·261)/4 = 1218.

**Checks.** The same method gives Q₄ = 18 and Q₅ = 52, and together with the axis counts these reproduce c₄ = 100 and c₅ = 284 exactly. The n = 8 axis counts were cross-checked by reflection/reversal symmetry of the x-path classes, but I have not independently verified N(2,0) and N(4,0) by a second full enumeration, so the 1218 rests on those hand counts.

ANSWER: 1218