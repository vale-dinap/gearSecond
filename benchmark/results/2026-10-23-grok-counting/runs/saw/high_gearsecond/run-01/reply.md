The walks are partitioned by \(k\), the common number of north and south steps. Then \(8-2k\) steps are horizontal, the net \(y\)-displacement is zero, and every lattice point is visited at most once.

- For \(k=0\) the walk lies on the \(x\)-axis, so the only self-avoiding possibilities are the two straight walks.  
- For \(k=4\) the walk lies on the \(y\)-axis and must reverse, which is impossible.  
- For \(k=1\) the single north step occurs before the single south step (or vice versa). Each horizontal run is necessarily monotone, and the unique run at height \(\pm1\) has positive length. Enumerating the admissible lengths and directions on each side of the axis produces 68 walks in the upper half-plane and 68 in the lower half-plane, hence 136 walks.  
- For \(k=3\) the two horizontal steps must point the same way (opposite directions always close a vertical line onto an already-visited site). The three vertical runs determined by those steps are monotone and the north steps total exactly three, giving 18 walks that finish at \(x=+2\) and 18 that finish at \(x=-2\), hence 36 walks.  
- For \(k=2\) the six possible orders of the two north and two south steps are examined separately. Immediate reversals force certain runs to have positive length; the remaining length distributions (a few dozen) are checked one-by-one for directional choices that keep all visits to each horizontal line disjoint. The six orders contribute
  \[
  122+122+10+10+42+42=348
  \]
  walks.

Adding these disjoint classes yields
\[
2+136+348+36=522.
\]

ANSWER: 522