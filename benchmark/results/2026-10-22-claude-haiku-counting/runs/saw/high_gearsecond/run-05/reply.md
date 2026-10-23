**Answer: 522**

Walks ending at (0,0) are impossible, so the endpoint is (x,0) with x even and nonzero. Symmetry under x → -x means I count x > 0 and double.

Counts by endpoint, split by the number of horizontal steps h = e + w:

- **(±8,0): 1 each.** All 8 steps must be E (or all W).
- **(±6,0): 42 each.** Either 6E+N+S, with N and S in different non-adjacent positions (42), or 7E+W, which is never self-avoiding. Total 42.
- **(±4,0): 126 each.**
  - h=4 (4E, 2N, 2S): the vertical moves split into 5 column blocks, each monotone. Count = 110.
  - h=6 (5E, W, N, S): the W must sit alone in its row segment. Eight valid horizontal-segment patterns, times 2 for N-first or S-first, gives 16.
  - h=8: 0.
- **(±2,0): 92 each.**
  - h=2 (2E, 3N, 3S): three columns with monotone vertical runs. Count = 18.
  - h=4 (3E, W, 2N, 2S): split by where the W falls among the four horizontal moves. The four patterns give 30, 2, 2, 30. A reversal-plus-reflection symmetry pairs the patterns as (30,30) and (2,2), which checks out.
  - h=6 (4E, 2W, N, S): five valid (D0, D1, D2) segment triples, times 2 for the vertical order, gives 10.
  - h=8: 0.

Total over the x-axis:

2 × (92 + 126 + 42 + 1) = 2 × 261 = **522**

The h=4 subcase for (±2,0) is the most error-prone part of the hand count. I checked its pattern symmetry but did not verify the total by a separate method or by code.

ANSWER: 522