The 8-step self-avoiding walks on the square lattice are equidistributed among the four open quadrants once the walks that terminate on the axes are removed. The total number of 8-step self-avoiding walks is 5916, so the desired count is
\[
(5916 - 4\sigma)/4,
\]
where \(\sigma\) is the number of walks that end on the positive \(x\)-axis.

The possible endpoints on that axis are \((2,0)\), \((4,0)\), \((6,0)\) and \((8,0)\). Direct enumeration by step-content (and, when a single west step is present, by the unique column in which that step occurs) yields
\[
\begin{align*}
A(8,0) &= 1,\\
A(6,0) &= 42,\\
A(4,0) &= 126,\\
A(2,0) &= 82.
\end{align*}
\]
Hence \(\sigma = 251\). The number of walks ending in the open first quadrant is therefore
\[
(5916 - 4\cdot 251)/4 = 1228.
\]

ANSWER: 1228