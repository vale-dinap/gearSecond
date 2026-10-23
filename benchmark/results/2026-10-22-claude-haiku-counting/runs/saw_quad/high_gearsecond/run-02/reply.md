The count is **1218**. I worked it out by hand from the known total c₈ = 5916, without code.

**Method.** Walks ending on an axis, or at the origin, are not counted in the quadrant count. The origin is impossible because a closed walk revisits its start. Let S = N(2,0)+N(4,0)+N(6,0)+N(8,0), where N(k,0) counts walks ending at (k,0). By the eight-fold symmetry of the square lattice, the axis endpoints total 4S, and the four open quadrants have equal counts. So the answer is (5916 − 4S)/4.

**Axis counts** (by step-type decomposition of each endpoint):
- N(8,0) = 1 (straight line).
- N(6,0) = 42 (six E, one N, one S, with the N and S columns ordered: C(7,2) × 2).
- N(4,0) = 126: 110 walks with E4 N2 S2 (column model) plus 16 with E5 W1 N1 S1.
- N(2,0) = 92: 18 with E2 N3 S3, plus 64 with E3 W1 N2 S2 (over the four horizontal orderings), plus 10 with E4 W2 N1 S1.

So S = 92 + 126 + 42 + 1 = 261.

**Result:** (5916 − 4·261)/4 = (5916 − 1044)/4 = 4872/4 = 1218.

ANSWER: 1218