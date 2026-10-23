The 8-step self-avoiding walks that end on the \(x\)-axis are partitioned by the number \(k\) of north steps (equivalently south steps). The endpoint condition and self-avoidance force \(k\in\{0,1,2,3\}\).

- For \(k=0\) the only surviving walks are the two straight walks along the axis.
- For \(k=1\) each walk consists of a single height-1 excursion. The three horizontal runs must be unidirectional; imposing the resulting non-overlap conditions on the line yields 68 walks that stay in the upper half-plane and 68 that stay in the lower half-plane, for a total of 136.
- For \(k=2\) the possible orders of the four vertical steps fall into three geometric types:
  - walks that reach height 2 (order NNSS or SSNN) — 122 per side, hence 244;
  - walks that make two disjoint height-1 excursions on the same side of the axis — 10 per side, hence 20;
  - walks that make one excursion on each side of the axis — 42 for each of the two mixed orders, hence 84.
  The three types are exhaustive and disjoint, giving 348 walks.
- For \(k=3\) both horizontal steps must point the same way (otherwise the walk closes). In each column the vertical run is necessarily monotone, and the admissible distributions of the three north and three south steps among the three columns produce 18 walks for each horizontal direction, hence 36 walks.
- For \(k=4\) every walk is confined to a single vertical line and therefore revisits a vertex.

Adding these contributions produces the total
\[
2+136+348+36=522.
\]

ANSWER: 522