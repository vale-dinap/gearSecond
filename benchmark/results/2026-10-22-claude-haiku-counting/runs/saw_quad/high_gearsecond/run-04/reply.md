Total 8-step SAWs: c₈ = 5916 (a known value, recalled rather than derived here). By the 8-fold symmetry of the square lattice, the count is 5916 = (axis endpoints) + 4 × (open-quadrant endpoints), so I counted the walks ending on the positive x-axis.

Endpoints on the positive x-axis must have even x. Counting by step composition:

- **(8,0):** 1 walk (straight line).
- **(6,0):** 42 walks (6E, 1N, 1S; the N/S excursion can start and end at any pair of columns i < j, in either order).
- **(4,0):** 126 walks (110 with 4E, 2N, 2S; 16 with 5E, 1W, 1N, 1S).
- **(2,0):** 92 walks (18 with 2E, 3N, 3S; 64 with 3E, 1W, 2N, 2S; 10 with 4E, 2W, 1N, 1S).

The sum over the positive x-axis is 1 + 42 + 126 + 92 = 261, so the four axis directions contribute 4 × 261 = 1044 walks.

The open-quadrant count per quadrant is therefore (5916 − 1044) / 4 = 4872 / 4 = 1218.

The same method gives 18 for length 4 and 2 for length 2, which match direct enumeration. The (2,0) count of 92 is the most error-prone part; the reversal symmetry check on the horizontal step order passed, but I did not verify the full total against an independent source.

ANSWER: 1218