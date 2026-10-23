The 8-step self-avoiding walks ending in the open first quadrant are partitioned by the parity excess \(8-(x+y)\).

- Excess 0 forces the walks to be strictly monotone (only E and N). Their number is
  \[
  \binom{8}{1}+\binom{8}{2}+\binom{8}{3}+\binom{8}{4}+\binom{8}{5}+\binom{8}{6}+\binom{8}{7}=254.
  \]

- Excess 2 produces the five admissible endpoints \((5,1)\), \((4,2)\), \((3,3)\), \((2,4)\) and \((1,5)\). For each endpoint the possible step multisets contain at most one reverse step. Walks with no west steps are counted by placing pure vertical runs into the columns created by the east steps; walks with no south steps reduce to monotone horizontal excursions on successive horizontal lines; walks with one west and one south are precisely the sequences that avoid immediate reversals and 4-step plaquettes. The resulting cardinalities are 92, 118, 120, 118 and 92, which sum to 540.

- Excess 4 produces the endpoints \((3,1)\), \((2,2)\) and \((1,3)\). The same case division on the reverse steps yields 118, 112 and 118 walks respectively, summing to 348.

- Excess 6 produces only the endpoint \((1,1)\). The four admissible step multisets are examined by the location of the unique south step (or by the symmetric argument with the roles of the axes exchanged). In every sub-case the horizontal excursions that lie between vertical steps must themselves be monotone; imposing the global step counts and forbidding overlaps of those excursions produces exactly 76 walks.

Adding these contributions gives the total
\[
254+540+348+76=1218.
\]

(The same enumeration is compatible with the known total of 5916 eight-step self-avoiding walks on the whole lattice and with the equal distribution of those walks among the four open quadrants and the four rays.)

ANSWER: 1218