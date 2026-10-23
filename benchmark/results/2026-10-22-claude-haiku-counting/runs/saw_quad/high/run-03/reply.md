**Approach:** Use the 90° rotation and reflection symmetries of the square lattice to reduce the count to walks ending on the positive x-axis.

Let Q be the number of 8-step SAWs ending in the open quadrant x>0, y>0, and A the number ending on the positive x-axis. By symmetry, each open quadrant holds Q walks and each half-axis holds A, so

c₈ = 4Q + 4A,

where c₈ = 5916 is the known total number of 8-step SAWs on the square lattice (recalled, not recomputed here).

**Counting A.** An 8-step walk ending at (x,0) has x even. Write e, w, n, s for the numbers of E, W, N, S steps, with n = s = k.

- **(8,0):** only EEEEEEEE, so 1.
- **(6,0):** k=1 gives 6E, N, S. The N and S sit in different columns, with the N column before the S column or vice versa, giving 7·6 = 42.
- **(4,0):**
  - k=1 (5E, 1W, 1N, 1S): the single W must lie on a row-0 segment, and the excursion row must be monotone. This gives 8 walks for each vertical direction, so 16.
  - k=2 (4E, 2N, 2S): the x-coordinate is monotone, so each column's vertical run is monotone. Counting integer run vectors with total |r| = 4 and Σr = 0 over 5 columns gives 110.
  - Total: 126.
- **(2,0):**
  - k=1 (4E, 2W, 1N, 1S): 5 valid placements per vertical direction, so 10.
  - k=2 (3E, 1W, 2N, 2S): split by the six N/S orderings. Ordering NNSS (and its mirror) gives 26 each, NSSN (and its mirror) gives 6 each, and NSNS (and its mirror) gives 0. Total 64.
  - k=3 (2E, 3N, 3S): column-run counting gives 18.
  - Total: 92.

So A = 92 + 126 + 42 + 1 = 261.

**Result.**

Q = (5916 − 4·261)/4 = 1479 − 261 = 1218.

As a check on the method, the same decomposition reproduces c₃ = 36 and c₄ = 100 and gives Q₂ = 2, Q₃ = 6, Q₄ = 18, which agree with direct enumeration.

ANSWER: 1218