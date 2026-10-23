The endpoint of an 8-step walk lies on the diagonal if and only if it is one of the points \((k,k)\) with \(|k|\le 4\). The case \(k=0\) is impossible: the nine lattice points of an 8-step walk are distinct, so the walk cannot return to the origin. Reflection through the origin interchanges the counts for \(k\) and \(-k\), so it is enough to treat \(k>0\) and double.

Write \(E,W,N,S\) for the number of steps of each type. The conditions \(E-W=N-S=k\) and \(E+W+N+S=8\) force \(W+S=4-k\). For each admissible pair \((W,S)\) the self-avoiding realisations are counted by decomposing the walk into horizontal (or vertical) excursions separated by the steps that change row (or column). On the line an excursion is self-avoiding if and only if it is monotone, and a return to a previously visited row or column is possible only at a \(y\)-coordinate (respectively \(x\)-coordinate) lying outside the interval already occupied. These constraints are expressed by linear inequalities on the lengths of the excursions; the number of non-negative integer solutions is given by stars-and-bars.

- \(k=4\): only \(4\) east and \(4\) north. All \(\binom{8}{4}=70\) sequences are self-avoiding.
- \(k=3\): the two step-types \((W,S)=(1,0)\) and \((0,1)\). Each contributes 60 walks, for a total of 120.
- \(k=2\): the three step-types \((W,S)=(2,0)\), \((0,2)\) and \((1,1)\). They contribute 18, 18 and 76 walks respectively, for a total of 112.
- \(k=1\): the four step-types \((W,S)=(3,0)\), \((0,3)\), \((1,2)\) and \((2,1)\). They contribute 2, 2, 36 and 36 walks respectively, for a total of 76.

Adding these contributions yields
\[
70+120+112+76=378
\]
walks with positive \(k\). The same number end at a negative diagonal point, so the total is \(2\times 378=756\).

ANSWER: 756