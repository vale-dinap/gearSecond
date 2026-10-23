**Answer: 1218**

**Approach.** The total number of 8-step self-avoiding walks on the square lattice is c₈ = 5916 (a known value, not re-derived here). Use the symmetries of the square:

- The four open quadrants are related by reflections, so they contain equal numbers of walks.
- The x-axis and y-axis endpoints are related by swapping x and y, so they also contain equal numbers.
- The origin is never an endpoint, since that would revisit it.

Let N(k) be the number of walks ending at (k, 0) for k > 0, and let S = N(2) + N(4) + N(6) + N(8). Then the axis endpoints account for 4S walks, and

(5916 − 4S) / 4 = 1479 − S.

**Axis counts.** Parity forces even k, and E − W = k with the vertical steps balancing:

- **N(8) = 1:** the straight line.
- **N(6) = 42:** six E steps plus one N and one S in distinct columns, giving 7·6 = 42.
- **N(4) = 126:**
  - 4E, 2N, 2S (no W): 110. This counts ways to place N-runs and S-runs in five columns with disjoint supports.
  - 5E, 1W, 1N, 1S: 16, by case analysis on the position of the W step and the N/S detour.
- **N(2) = 92:**
  - 2E, 3N, 3S: 18 (three columns, runs of 3 with disjoint supports).
  - 3E, 1W, 2N, 2S: 64. This splits into six vertical patterns, with counts 26, 0, 6 for the first three and mirror symmetry for the rest.
  - 4E, 2W, 1N, 1S: 10 (five valid walks for each of the two vertical orders).

So S = 1 + 42 + 126 + 92 = 261, and the answer is 1479 − 261 = 1218.

**Checks.** The same decomposition reproduces the quadrant counts for n = 3 (6 per quadrant, 36 total) and n = 4 (18 per quadrant, matching (100 − 28)/4). The N(2) and N(4) case analyses were done by hand and are the most error-prone part, so treat 1218 as carefully derived rather than machine-verified.

ANSWER: 1218