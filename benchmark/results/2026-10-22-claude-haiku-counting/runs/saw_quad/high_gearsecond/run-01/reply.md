**Answer: 1218**

**Method.** The square lattice has 5916 eight-step SAWs (known total, A001411). Split them by endpoint:

- Endpoints on the axes are (±a,0) and (0,±a) with a even. Let A_a be the count ending at (a,0). Each of the 4 axis points at distance a has count A_a, so the axis total is 4·ΣA_a.
- The four open quadrants are symmetric, so each holds Q walks. The total is 5916 = 4Q + 4·ΣA_a.

**Axis counts (by hand):**

- **A_8 = 1** (straight line).
- **A_6 = 42.** Steps are 6E, 1N, 1S. The N and S detour must be separated by at least one E, giving 21 orderings, times 2 for N/S order.
- **A_4 = 126.** Two cases:
  - 4E, 2N, 2S (no W): column-run count gives 110.
  - 5E, 1W, 1N, 1S: row-segment count gives 16.
- **A_2 = 92.** Three cases:
  - 2E, 3N, 3S: 18.
  - 3E, 1W, 2N, 2S: 64.
  - 4E, 2W, 1N, 1S: 10.

Each case was enumerated by splitting the walk into horizontal runs between vertical moves, checking that runs in the same row don't overlap.

**Totals.** ΣA_a = 92 + 126 + 42 + 1 = 261.

4Q = 5916 − 4·261 = 4872, so Q = 1218.

**Check.** The same method at n = 4 gives A_2 = 6, A_4 = 1, and Q = 18, which reproduces c_4 = 100.

The A_2 and A_4 subcounts are the error-prone parts. I checked the sub-cases twice, but I did not verify them by computer, as you asked.

ANSWER: 1218