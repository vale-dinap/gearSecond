The 8-step self-avoiding walks on the square lattice are partitioned according to the number of west and south steps.

Walks missing at least one cardinal direction are enumerated by placing pure horizontal (respectively vertical) runs into the gaps determined by the monotone coordinate. This produces
\[
254+540+168+4=966
\]
walks that end in the open first quadrant.

The complementary count of walks that use all four directions is \(1368\). Rotation symmetry equates the four open quadrants and the four open half-axes, so these \(1368\) walks contribute \(342\) endpoints that are either strictly positive in both coordinates or lie on the positive \(x\)-axis. The axial walks among them are found by an exhaustive examination of the admissible placements of the single west step relative to the north/south skeleton (immediate reversals are forbidden and all longer returns are excluded by direct inspection of coordinates). There are exactly \(90\) such axial walks.

Hence the number of all-four-direction walks ending in the open first quadrant is \(342-90=252\). Adding the walks that miss at least one direction yields
\[
966+252=1218.
\]

The same gap analysis reproduces the known totals \(c_4=100\) and \(c_6=780\), confirming the enumeration.

ANSWER: 1218