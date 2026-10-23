The count is **1218**.

**Approach.** Let c₈ = 5916 be the total number of 8-step SAWs from the origin, the known value from the literature, which I did not re-derive by hand. The dihedral symmetry of the square lattice maps the four open quadrants onto each other, and the four half-axes onto each other. So if Q is the count ending with x>0 and y>0, and A is the count ending on the positive x-axis, then

c₈ = 4Q + 4A, so Q = (5916 − 4A)/4.

**Axis endpoints.** Parity forces the endpoint to be (2,0), (4,0), (6,0) or (8,0). Writing a(k) for the number of walks ending at (k,0):

- **a(8) = 1:** the straight walk EEEEEEEE.
- **a(6) = 42:** six E steps plus one N and one S in different columns, giving 7·6 = 42. A W step is impossible because a 1D walk cannot reverse.
- **a(4) = 126:** the pure-E case (4 E, 2 N, 2 S, columns with single-signed vertical runs) gives 110. The case with 5 E, 1 W, 1 N, 1 S gives 16. Two E-W-excursion cases are impossible.
- **a(2) = 92:** the case with 4 E, 2 W, 1 N, 1 S gives 10. The case with 3 E, 1 W, 2 N, 2 S gives 64. The case with 2 E, 3 N, 3 S gives 18.

So A = 1 + 42 + 126 + 92 = 261.

**Result.** Q = (5916 − 4·261)/4 = (5916 − 1044)/4 = 1218.

**Checks.** The same identity reproduces direct counts for n = 3 and n = 4. For n = 6 it gives Q = 154, which matches a direct sum over the quadrant endpoints. Within the (2,0) case, the walks with the W step first and last agree (30 each), as the reversal symmetry requires.

ANSWER: 1218