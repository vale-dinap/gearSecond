The parity of an 8-step walk forces any endpoint on the \(x\)-axis to be one of \((\pm 2,0)\), \((\pm 4,0)\), \((\pm 6,0)\), \((\pm 8,0)\). The origin is impossible: returning there repeats the starting vertex. Reflection \(E\leftrightarrow W\) pairs the positive and negative endpoints, so it is enough to count walks to \(x>0\) and double.

Write \(E,W,N,S\) for the step counts. Self-avoidance on a single row or column forces every horizontal sojourn to be monotone, so a sojourn that uses both \(E\) and \(W\) is impossible. With that constraint the walks fall into a few step-types.

**Endpoint \((8,0)\).** Only \(E^8\). Count: \(1\).

**Endpoint \((6,0)\).** The only possible content is \(6E+1N+1S\) (the content \(7E+1W\) is confined to the \(x\)-axis and must reverse). The unique north step and unique south step are separated by \(b\ge 1\) east steps, with \(a\) east steps before the first vertical step and \(c\) after the second, \(a+b+c=6\). Every such walk is self-avoiding, and there are \(21\) placements for each order \(NS\) and \(SN\). Count: \(42\).

**Endpoint \((4,0)\).**
- \(4E+2N+2S\). There is no west step, so each vertical coordinate \(x=0,1,2,3,4\) is visited in a single straight sojourn. The sojourn lengths are a 5-tuple of signed integers in \(\{-2,-1,0,1,2\}\) with positive parts summing to \(2\) and negative parts summing to \(2\). There are \(110\) such tuples, and each determines one self-avoiding walk.
- \(5E+1W+1N+1S\). The height is in \(\{0,1\}\) or \(\{0,-1\}\). In the nonnegative case the single west step occupies one sojourn and the five east steps occupy the others. Exactly \(8\) placements avoid overlaps (and likewise \(8\) for the nonpositive case).
- \(6E+2W\) lies on the axis and cannot be self-avoiding.

Count: \(110+16=126\).

**Endpoint \((2,0)\).**
- \(2E+3N+3S\). Again there is no west step, so the three columns \(x=0,1,2\) are straight sojourns. The signed lengths with three steps up and three steps down number \(18\), each giving one self-avoiding walk.
- \(4E+2W+1N+1S\). The same three-sojourn analysis as above, now with two west steps, yields \(5\) nonnegative walks and \(5\) nonpositive walks. Count: \(10\).
- \(3E+1W+2N+2S\). The six orders of \(\{N,N,S,S\}\) determine the horizontal sojourns. Distributing one west step and three east steps into those sojourns and discarding overlaps gives \(26\) walks for \(NNSS\), \(26\) for \(SSNN\), \(6\) for \(NSSN\), \(6\) for \(SNNS\), and none for \(NSNS\) or \(SNSN\). Count: \(64\).
- \(5E+3W\) is purely horizontal, hence not self-avoiding.

Count: \(18+10+64=92\).

**Total.** Doubling the positive endpoints and adding the two full-length rays,
\[
2(1+42+126+92)=522.
\]

ANSWER: 522