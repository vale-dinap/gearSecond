The count is **756**: the walk must end at (a,a) with a ∈ {−4,…,4}, and each endpoint count is below.

| Endpoint (a,a) | Count |
|---|---|
| (0,0) | 0 (the walk would revisit the origin) |
| (±1,±1) | 76 each |
| (±2,±2) | 112 each |
| (±3,±3) | 120 each |
| (±4,±4) | 70 each |

Each count is the number of 8-step words whose step counts give the endpoint and which have no contiguous zero-sum factor (a contiguous factor with equal E/W and equal N/S counts would revisit a point).

- **(4,4):** the walk must use only E and N steps, 4 of each, so every arrangement is self-avoiding: C(8,4) = 70.
- **(3,3):** the step counts are either 4E,1W,3N or 3E,4N,1S (mirror images). In the first, the single W must not be adjacent to an E, giving 60 words; the mirror case also gives 60. Total 120.
- **(2,2):** the step counts split into 4E,2W,2N (18 words), its mirror 2E,4N,2S (18 words), and 3E,1W,3N,1S (76 words). Total 112. The 76 was checked by two independent methods.
- **(1,1):** the step counts split into 4E,3W,1N (2 words), its mirror (2 words), 3E,2W,2N,1S (36 words), and its mirror (36 words). Total 76.

Summing over the eight endpoints: 2 × (76 + 112 + 120 + 70) = 756.

ANSWER: 756