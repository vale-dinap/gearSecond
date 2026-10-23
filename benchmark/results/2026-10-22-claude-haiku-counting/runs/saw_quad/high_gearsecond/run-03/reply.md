**Method.** Let c₈ = 5916 be the total number of 8-step SAWs. By the 8-fold symmetry of the square lattice, the four open quadrants have equal counts Q, and the four positive half-axes have equal counts B, so c₈ = 4Q + 4B. The question asks for Q, so Q = 1479 − B, where B = N(2,0) + N(4,0) + N(6,0) + N(8,0) and N(x,0) is the number of walks ending at (x,0).

**Axis counts.**
- N(8,0) = 1 (straight line).
- N(6,0) = 42: steps are 6E, 1N, 1S, and the vertical excursion can go up or down, giving 2 × C(7,2) = 42.
- N(4,0) = 126: the case with 5E, 1W, 1N, 1S gives 16, and the case with 4E, 2N, 2S (monotone in x, so a column-by-column height sequence) gives 110.
- N(2,0) = 92: the case with 2E, 3N, 3S gives 18; the case with 3E, 1W, 2N, 2S gives 64; the case with 4E, 2W, 1N, 1S gives 10.

So B = 1 + 42 + 126 + 92 = 261.

**Check of the method.** The same decomposition gives c₄ = 4·18 + 4·7 = 100, which matches the known value and a direct count of the first-quadrant walks.

**Result.** Q = 1479 − 261 = 1218.

The axis counts were done by hand with case analysis, so the value is only as reliable as those case counts. I did not verify N(2,0) = 92 against an independent table.

ANSWER: 1218