Endpoint must be (x, 0) with x ≠ 0, since the origin is already visited. Parity forces x even, so x ∈ {±2, ±4, ±6, ±8}. By reflection symmetry, count one side and double.

**Counts by endpoint (x, 0), by step multiset:**

- **(8, 0):** all E. **1**
- **(6, 0):** {E×6, N, S}. The walk is E^a N E^k S E^r with k ≥ 1 and a + k + r = 6, giving 21. Doubled for S-first: **42**.
- **(4, 0):**
  - {E×6, W×2}: impossible (a 1D walk must be monotone). **0**
  - {E×5, W, N, S}: **16**
  - {E×4, N×2, S×2}: each column's vertical run must be monotone, so the count is 110 (confirmed two ways). **110**
  - Total **126**
- **(2, 0):**
  - {E×5, W×3}: impossible. **0**
  - {E×4, W×2, N, S}: **10**
  - {E×3, W, N×2, S×2}: split by vertical pattern (NNSS, NSNS, NSSN, and mirrors) and by which horizontal run holds the W. Totals are 26, 0, 6 per pattern, mirrored, giving **64**
  - {E×2, N×3, S×3}: **18**
  - Total **92**

**Total:**

2 × (1 + 42 + 126 + 92) = 2 × 261 = **522**

These were counted by hand. The n = 4 analogue checks out (14 endpoints on the axis), and the mirror-symmetric subcases match, but the (2, 0) multi-W case is the most error-prone part.

ANSWER: 522