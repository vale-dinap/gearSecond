**Answer: 522**

By symmetry, the count is 2·(N₂ + N₄ + N₆ + N₈), where Nₖ is the number of 8-step SAWs ending at (k,0). Endpoints must have even x, and (0,0) is impossible.

Each walk has E−W = k and N = S = s, with 8 = E + W + 2s. Split by (W, s):

- **N₈ = 1.** Only all-E.
- **N₆ = 42.** Options are (W,s) = (0,1) or (1,0). The (1,0) case is one-dimensional and impossible. In (0,1), the walk has 6 E steps, and the N and S steps must lie in distinct columns among the 7 columns. That gives 7·6 = 42.
- **N₄ = 126.** Options are (0,2), (1,1), (2,0).
  - (0,2): 4E, 2N, 2S. Each column's vertical run must be single-signed. This is the coefficient of x²y² in (1+u+v)⁵ with u = x/(1−x), v = y/(1−y), which is 110.
  - (1,1): 5E, 1W, 1N, 1S. The single W forces a shared-column check on the x-repeats. This gives 16.
  - (2,0): one-dimensional, impossible.
- **N₂ = 92.** Options are (0,3), (1,2), (2,1), (3,0).
  - (0,3): 2E, 3N, 3S. Same column method gives 18.
  - (1,2): 3E, 1W, 2N, 2S. Case analysis over the W position gives 30 + 2 + 2 + 30 = 64. The 30s and 2s are paired by reversal symmetry, which maps W position m to 5−m.
  - (2,1): 4E, 2W, 1N, 1S. Checking all 15 horizontal words gives 10.
  - (3,0): impossible.

Total: 2·(92 + 126 + 42 + 1) = 2·261 = 522.

The enumeration was done by hand, so the larger sub-counts (64 and 10) carry the most risk. I checked the method on small cases (4-step walks to (2,0) give 6, which matches direct listing) and used the reversal symmetry as a consistency check.

ANSWER: 522