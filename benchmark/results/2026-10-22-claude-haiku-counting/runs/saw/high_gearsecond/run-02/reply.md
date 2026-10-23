The count is **522**: 261 walks end on the positive x-axis, and by reflection in the y-axis another 261 end on the negative x-axis.

Walks of 8 steps ending at (x, 0) need x even and x ≠ 0. Let N(x) be the count ending at (x, 0), so N(±x) = N(x).

- **N(8) = 1:** only EEEEEEEE.
- **N(6) = 42:** the steps are 6E, 1N, 1S. The N and S must sit in different columns a < b, with the first vertical at column a. That gives 2 · C(7,2) = 42.
- **N(4) = 126:** the step types are 4E,2N,2S (110 walks) or 5E,1W,1N,1S (16 walks). The 6E,2W case is one-dimensional and impossible.
- **N(2) = 92:** the step types are 4E,2W,1N,1S (10 walks), 3E,1W,2N,2S (64 walks), or 2E,3N,3S (18 walks). The 5E,3W and 2E... cases with no vertical steps are one-dimensional and impossible.

The W-containing counts were checked two ways each: by splitting the walk at its single W step, and by reflection-reversal symmetry (which pairs the counts for c and 3−c E-steps before the W in the 4E,2W,... case).

Total: 2 × (92 + 126 + 42 + 1) = 522.

ANSWER: 522