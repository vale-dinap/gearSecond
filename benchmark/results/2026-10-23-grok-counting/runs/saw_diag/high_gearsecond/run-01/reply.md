The endpoint of an 8-step walk lies on the diagonal if and only if it is one of the lattice points \((k,k)\) with \(|k|\le 4\). A self-avoiding walk cannot return to the origin, so the case \(k=0\) contributes nothing. Rotational symmetry identifies the counts for \(k\) and \(-k\), and it is therefore enough to treat \(k>0\).

Write \(e,w,n,s\) for the number of steps of each type. The conditions \(e-w=n-s=k\) and \(e+w+n+s=8\) force the non-negative integer solutions to be examined by the value of \(k\).

- For \(k=4\) the only possibility is four east and four north steps. Every such sequence is self-avoiding, giving \(\binom{8}{4}=70\) walks.
- For \(k=3\) the two symmetric possibilities are \((e,w,n,s)=(3,0,4,1)\) and \((4,1,3,0)\). In the first family the abscissa is non-decreasing, so the walk decomposes into four vertical sojourns. A sojourn on the line is self-avoiding if and only if it is monotone, which forces the single south step to occupy a sojourn by itself. There are exactly 60 such walks; the reflected family contributes another 60, for a total of 120.
- For \(k=2\) the three families are \((2,0,4,2)\), \((4,2,2,0)\) and \((3,1,3,1)\). The first family again has non-decreasing abscissa. Monotonicity of each vertical sojourn produces exactly 18 walks; reflection supplies the second family of 18. For the third family the single west step may occur in four possible orders relative to the three east steps. In each order the walk decomposes into vertical sojourns, some of which may return to a previously visited vertical line. Each sojourn must be monotone and the sets of ordinates visited on repeated visits to the same abscissa must be disjoint. Enumerating the admissible distributions of the single south step yields \(32+6+6+32=76\) walks. The three families together give 112 walks.
- For \(k=1\) the four families are \((1,0,4,3)\), \((4,3,1,0)\), \((2,1,3,2)\) and \((3,2,2,1)\). The same sojourn analysis produces 2 walks in each of the first two families and 36 walks in each of the last two, for a total of 76 walks.

Doubling to include negative \(k\) therefore produces
\[
2(70+120+112+76)=756.
\]

ANSWER: 756