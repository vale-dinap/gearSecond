The count is **1218**, worked out by hand with no code.

**Symmetry reduction.** The total number of 8-step SAWs is c₈ = 5916. The endpoint can't be the origin, and the eight symmetries of the square lattice split the endpoints into four open quadrants (each with count A, which includes diagonal points), four positive or negative half-axes (each with count B), and nothing else. So 4A + 4B = 5916, giving A + B = 1479.

**Half-axis count.** B = N(2,0) + N(4,0) + N(6,0) + N(8,0), where N(x,0) is the number of 8-step SAWs ending at (x,0).

- **N(8,0) = 1:** all E.
- **N(6,0) = 42:** the steps are six E's plus one N and one S. The vertical excursion can go up or down, and the N and S positions give 7·6 = 42 walks.
- **N(4,0) = 126:** split by step content.
  - Four E's, two N's, two S's: the walk visits 5 columns, each with a monotone vertical run. This gives 110.
  - Five E's, one W, one N, one S: 16 (checked by segment analysis).
- **N(2,0) = 92:** split by step content.
  - Two E's, three N's, three S's: 18.
  - Four E's, two W's, one N, one S: 10.
  - Three E's, one W, two N's, two S's: 64. This is split by the position of the single W, and the vertical-run disjointness conditions were checked by two independent enumerations.

So B = 92 + 126 + 42 + 1 = 261.

**Result.** A = 1479 − 261 = 1218.

**Method check.** The same decomposition reproduces c₄ = 100 and c₆ = 780 exactly, including the W-containing cases at n = 6.

ANSWER: 1218