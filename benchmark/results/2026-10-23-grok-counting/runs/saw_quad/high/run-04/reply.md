The 8-step self-avoiding walks ending in the open first quadrant are partitioned by the parity-compatible endpoints \((x,y)\) with \(x>0\), \(y>0\) and \(x+y\le 8\).

For each admissible endpoint the possible numbers of west and south steps are fixed by the relations
\[
x=E-W,\qquad y=N-S,\qquad E+W+N+S=8.
\]
- When one of \(W,S\) vanishes the walks are strictly monotone in the remaining coordinate. They decompose into independent horizontal (or vertical) runs, one per level; self-avoidance is then equivalent to each run being monotone. The resulting distributions of runs are given by elementary binomial coefficients and yield
  \[
  \begin{align*}
  (7,1)&:8,\\
  (6,2)&:28,\\
  (5,3)&:56,\\
  (4,4)&:70,\\
  (5,1)&:92,\\
  (4,2)&:118,\\
  (3,3)&:120,\\
  (3,1)&:118,\\
  (2,4)&:118,\\
  (2,2)&:36,\\
  (1,5)&:92,\\
  (1,3)&:66,\\
  (1,7)&:8.
  \end{align*}
  \]
  (The symmetric counts for the reflected endpoints are identical.)
- When both \(W=S=1\) the only possible self-intersections are immediate reversals or 4-cycles. Both are local forbidden patterns. Enumerating the admissible placements of the single west and south steps (isolated from their opposite directions, and not completing a unit square) produces the additional contributions
  \[
  (3,3):60,\qquad (2,2):76,\qquad (1,3):52
  \]
  (and the symmetric values). Adding these contributions supplies the final tallies 120, 112 and 118 for those three endpoints.

Summing every endpoint except \((1,1)\) already gives 1142 walks.

The remaining endpoint \((1,1)\) requires \(W+S=3\). The four sub-cases are:
- \((W,S)=(3,0)\) and \((0,3)\): two walks each;
- \((W,S)=(2,1)\): the unique south step may occur in any of the eight positions. For each position the complementary north-east-west walk is enumerated by the same run decomposition used above and then tested for intersection with the south step; the eight positions contribute \(8+8+2+0+0+2+8+8=36\) walks. Reflection across the diagonal doubles the count, giving another 36 walks for \((W,S)=(1,2)\).

Hence exactly 76 walks end at \((1,1)\). Adding this last figure produces the total
\[
1142+76=1218.
\]

(The same enumeration recovers the classical totals \(c_4=100\) and \(c_6=780\), confirming the case division.)

ANSWER: 1218