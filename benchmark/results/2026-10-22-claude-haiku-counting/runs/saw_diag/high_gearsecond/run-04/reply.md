Walks ending on y = x must end at (a,a) with 2|a| ≤ 8. The origin is impossible (a SAW can't revisit its start), so a ∈ {±1, ±2, ±3, ±4}. The 180° rotation maps endpoint (a,a) to (−a,−a), so the count is twice the sum over a = 1 to 4.

Counts per endpoint, by letter-multiset (E, W, N, S):

- **(4,4): 70.** Only E and N steps, so C(8,4) = 70 monotone walks.
- **(3,3): 120.** Either 4E, 1W, 3N (60 walks: the W must not be adjacent to an E) or the transpose (60).
- **(2,2): 112.** 4E, 2W, 2N (18); 3E, 1W, 3N, 1S (76, checked by two independent methods); and the transpose of the first case (18).
- **(1,1): 76.** 1E, 4N, 3S (2); 2E, 1W, 3N, 2S (36, from the column-run decomposition, with the EWE pattern giving 0); 3E, 2W, 2N, 1S (36); and the transpose of the first case (2).

Sum over a = 1 to 4: 76 + 112 + 120 + 70 = 378. Doubling for a = ±: 2 × 378 = 756.

ANSWER: 756