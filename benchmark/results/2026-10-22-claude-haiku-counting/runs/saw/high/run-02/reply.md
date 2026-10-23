**Answer: 522**

Walks can't end at the origin, since that revisits the start point. Parity forces x to be even, so the endpoint is (x, 0) with x ∈ {±2, ±4, ±6, ±8}. Reflection x → −x gives N(x) = N(−x), so the total is 2·[N(2) + N(4) + N(6) + N(8)].

Let N(x) be the number of walks ending at (x, 0). Write k for the number of N steps, which equals the number of S steps, so there are 8 − 2k horizontal steps.

**N(8) = 1.** The walk must be E⁸.

**N(6) = 42.** The steps are 6 E, 1 N, 1 S. The walk never moves west, so each N/S pair lies in different columns, which means N and S cannot be adjacent. Ordered placements of N and S among 8 positions with |i−j| ≥ 2 give 42.

**N(4) = 126.**
- k = 2 (4 E, 2 N, 2 S, no W): each column's vertical run must be all-N or all-S, and the runs are spread over 5 columns. Counting column assignments gives 110.
- k = 1 (5 E, 1 W, 1 N, 1 S): I counted the N-before-S case by positions of the W and got 8. The S-before-N case is the mirror image, so 16 in total. I checked this with a second method (interval-disjointness on the row segments), which also gave 8 per order.
- Total: 16 + 110 = 126.

**N(2) = 92.**
- k = 3 (2 E, 3 N, 3 S): column-block counting gives 18.
- k = 1 (4 E, 2 W, 1 N, 1 S): the row-segment method gives 5 for the N-first pattern and 5 for the S-first pattern, so 10.
- k = 2 (3 E, 1 W, 2 N, 2 S): the 6 vertical patterns contribute UUDD 26, DDUU 26, UDDU 6, DUUD 6, UDUD 0, DUDU 0, so 64. This part rests on one detailed case analysis, with spot checks but no second independent count.
- Total: 10 + 64 + 18 = 92.

**Total:** 2 · (92 + 126 + 42 + 1) = 2 · 261 = **522**

ANSWER: 522