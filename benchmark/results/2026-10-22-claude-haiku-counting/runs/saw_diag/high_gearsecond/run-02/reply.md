The count is **756**, found by hand case analysis (no code). Walks of length 8 can only end at (a,a) with |a| ≤ 4, and (0,0) is impossible because a self-avoiding walk cannot return to the origin.

By the symmetry (x,y) → (−x,−y), the counts for a and −a are equal. Let N_a be the number of walks ending at (a,a):

- **N₄ = 70.** All 8 steps must be 4 E and 4 N, so the walk is monotone: C(8,4) = 70.
- **N₃ = 120.** Two step-type cases (one extra W, or one extra S), each giving 60 by a row-by-row argument, so 2 × 60.
- **N₂ = 112.** Split by the number of extra W and S steps: (2 W, 0 S) gives 18, (0 W, 2 S) gives 18, and (1 W, 1 S) gives 76.
- **N₁ = 76.** Cases with 3 extra horizontal/vertical reversals: (3 W, 0 S) gives 2, (0 W, 3 S) gives 2, and (2 W, 1 S) and (1 W, 2 S) each give 36.
- **N₀ = 0.**

The total is 2 × (76 + 112 + 120 + 70) = 2 × 378 = 756.

The two most error-prone counts (the (1 W, 1 S) case for N₂ and the (2 W, 1 S) case for N₁) were checked by reversal symmetry, which maps the vertical-order subcases onto each other with matching counts.

ANSWER: 756