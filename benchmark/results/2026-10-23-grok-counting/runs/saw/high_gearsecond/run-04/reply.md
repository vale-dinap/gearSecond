The walks are classified by the number of vertical steps. With the endpoint on the x-axis, that number is even: \(0,2,4,6,\) or \(8\) steps among \(\{N,S\}\), split equally between \(N\) and \(S\).

**0 vertical steps.** The walk lies on the x-axis, so any reversal revisits a vertex. Only \(E^8\) and \(W^8\) survive: **2** walks.

**2 vertical steps (one \(N\), one \(S\)).** The walk makes a single excursion off the axis. The horizontal runs before, during, and after that excursion are straight, and the landing site and the final run must avoid the vertices already used on \(y=0\). Counting the positive excursions and doubling by the reflection \(y\mapsto -y\) gives **136** walks.

**4 vertical steps (two \(N\), two \(S\)).** The vertical order is one of \(NNSS\), \(SSNN\), \(NSNS\), \(SNSN\), \(NSSN\), \(SNNS\). In each case the four horizontal steps occupy the gaps between those vertical steps, and each gap-run is straight. Tracking the occupied \(x\)-intervals on each horizontal line:

- \(NNSS\): **122** walks, and **122** for the reflection \(SSNN\)
- \(NSNS\): **10** walks, and **10** for \(SNSN\)
- \(NSSN\): **42** walks, and **42** for \(SNNS\)

Total: **348**. (The same casework reproduces the exactly enumerable all-east subsets: 35, 5, and 15 respectively.)

**6 vertical steps (three \(N\), three \(S\), two horizontal).** One east and one west step would finish at the origin, which is already visited, so both horizontal steps have the same direction. Each vertical line is then visited in a single monotone run, and the run lengths must split as three \(N\) and three \(S\). There are 18 such walks with both steps east and 18 with both west: **36** walks.

**8 vertical steps.** The walk is confined to the y-axis, so it cannot contain both \(N\) and \(S\): **0** walks.

Adding these disjoint classes:

\[
2+136+348+36=522.
\]

ANSWER: 522