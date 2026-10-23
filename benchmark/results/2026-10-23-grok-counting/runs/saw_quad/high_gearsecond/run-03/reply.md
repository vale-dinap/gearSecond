The 8-step self-avoiding walks ending in the open first quadrant are partitioned by the number \(k=w+s\) of west and south steps (equivalently by the Manhattan length \(x+y=8-2k\)).

- For \(k=0\) the walks use only east and north steps. Every such walk is self-avoiding, and exactly 254 of them have both coordinates positive.
- For walks that use west steps but no south steps the \(y\)-coordinate is non-decreasing, so the walk decomposes into independent horizontal sojourns. Each sojourn must be unidirectional. Enumerating the admissible distributions of the west steps among the levels produces 356 walks; symmetry supplies the same number of walks that use south steps but no west steps. The pure north-east walks have been counted twice, so the walks missing at least one of the two negative directions total 966.
- For \(k=2\) one has \(w=s=1\). The only possible returns to a previously visited vertex are immediate reversals or unit squares. Both are forbidden subword conditions and can be counted by placing the unique west step and enforcing the shielding and square-free constraints, giving 180 walks.
- For \(k=3\) the admissible pairs are \((w,s)=(2,1)\) and \((1,2)\). The same return analysis (now also excluding certain length-6 subwords) together with an exhaustive examination of the possible clusters of the two west steps produces 36 walks of each type, hence 72 walks.

Adding these disjoint classes yields the total.

ANSWER: 1218