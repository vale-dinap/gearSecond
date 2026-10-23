The count is **522**, from a hand enumeration split by the number of vertical steps. Endpoint y = 0 means the walk has equal numbers of N and S steps, so the vertical steps come in N/S pairs.

**Setup.** A walk with 2k vertical steps (k N and k S) and 8 − 2k horizontal steps ends on y = 0. Each maximal horizontal run lies in one row, so it is a straight segment. Self-avoidance reduces to requiring that horizontal runs in the same row cover disjoint integer intervals. Vertical steps can't reverse immediately, so consecutive N/S moves with an empty run between them are forbidden.

**Breakdown by vertical steps (v):**

- **v = 0:** all E's or all W's, giving **2**.
- **v = 2** (one N, one S): the walk goes up then down, or down then up. Each half is counted by a 1-D interval-disjointness argument. Each half gives 68, so **136**. This matches a direct recount of the same case.
- **v = 4** (two N, two S, four horizontal): there are six N/S orderings. Mirror symmetry gives 2 × (NNSS + NSNS + NSSN) = 2 × (122 + 10 + 42) = **348**.
- **v = 6** (three N, three S, two horizontal): the two horizontal steps must go the same direction, putting the walk in three distinct columns. The vertical block lengths (p₀, p₁, p₂) must satisfy Σp = 0 and Σ|p| = 6, which has 18 solutions per horizontal direction. That gives **36**.
- **v = 8:** no endpoint on the axis, **0**.

**Total:** 2 + 136 + 348 + 36 = 522.

**Checks.** The same method gives 2, 2, 6, 14 for lengths 1–4, which I verified by direct enumeration. The v = 2 count was checked two ways. The v = 4 count is the largest and most error-prone part of the hand work, so treat 522 as carefully derived rather than machine-verified.

ANSWER: 522