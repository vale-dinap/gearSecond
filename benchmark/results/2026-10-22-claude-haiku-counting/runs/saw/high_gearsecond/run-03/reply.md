Total: **522**.

Walks ending at (x,0) must have even x, and no 8-step SAW returns to the origin, so the total is 2·[N(2,0) + N(4,0) + N(6,0) + N(8,0)], where N(x,0) counts walks ending at (x,0).

- **N(8,0) = 1:** only E⁸.
- **N(6,0) = 42:** the single vertical excursion is one N and one S, with 6 E steps. Each order (N before S, or S before N) gives C(7,2) = 21 valid placements.
- **N(4,0) = 126:** 16 walks with one N, one S, 5 E and 1 W (8 per vertical order), plus 110 walks with 4 E and 2 N and 2 S, which need each column's vertical moves to be monotone.
- **N(2,0) = 92:** 10 walks with one N, one S, 4 E and 2 W; 64 walks with 3 E, 1 W, 2 N, 2 S (by the position of the W: 30, 2, 2, 30, with the first and last cases mirror images under reversal); and 18 walks with 2 E and 3 N and 3 S.

Sum over x ≥ 0: 1 + 42 + 126 + 92 = 261, so the total is 2 × 261 = 522. The N(2,0) count is the most error-prone piece; I checked it against the reversal symmetry, but it was done by hand, not by enumeration.

ANSWER: 522