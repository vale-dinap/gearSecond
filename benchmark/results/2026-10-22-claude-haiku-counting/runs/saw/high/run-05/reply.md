The count is **522**. I worked it out by hand, splitting walks by step multiset and checking each sub-case by a second method.

The origin is excluded because a walk ending there revisits its starting point. Endpoints are (x, 0) with x even, and by symmetry N(x,0) = N(−x,0).

**Endpoints and counts** (N(x,0) = walks ending at (x,0)):

- **x = ±8:** only E⁸, so 1 each.
- **x = ±6:** steps {6E, N, S}. Without W steps, each column's vertical run must be monotone, so the N and S go in different columns among 7 columns: 7·6 = 42 each. The step set {7E, W} is impossible because a horizontal-only walk cannot reverse.
- **x = ±4:**
  - {4E, 2N, 2S}: 110 (column model, 5 columns).
  - {5E, W, N, S}: 16. The W must sit in a run that avoids revisits, which leaves 8 walks per vertical orientation, times 2 for N-first versus S-first.
  - {6E, 2W}: impossible.
  - Total 126 each.
- **x = ±2:**
  - {2E, 3N, 3S}: 18 (column model, 3 columns).
  - {4E, 2W, N, S}: 10.
  - {3E, W, 2N, 2S}: 64. Enumerated over all six orders of the vertical steps and the position of the W; the orders NNSS and SSNN give 26 each, NSSN and SNNS give 6 each, and NSNS and SNSN give 0.
  - {5E, 3W}: impossible.
  - Total 92 each.

**Total:** 2·(1 + 42 + 126 + 92) = 2·261 = **522**

ANSWER: 522