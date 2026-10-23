The count is **756**. I worked it out by hand, splitting by endpoint and using the step counts of each walk.

**Setup.** An 8-step walk ends at (a,a) with a ≠ 0 and |a| ≤ 4. The symmetry (x,y) ↦ (−x,−y) gives N(a,a) = N(−a,−a), so the total is 2·(N₁+N₂+N₃+N₄), where N_a counts walks ending at (a,a).

**Endpoint (4,4).** Manhattan distance 8 forces all steps to be E or N, giving C(8,4) = **70** walks.

**Endpoint (3,3).** The step counts are {4E,1W,3N} or its mirror {3E,4N,1S}. Each is equal by the swap symmetry. A walk is self-avoiding iff the W is not adjacent to an E. Counting by W's position gives 15+15+6·5 = 60 each, so N₃ = 2·60 = **120**.

**Endpoint (2,2).** The step-count classes are {4E,2W,2N}, its mirror {2E,4N,2S}, and {3E,1W,3N,1S}.
- {4E,2W,2N}: with two N's the walk splits into three rows, and each row's E/W run must be monochromatic. Counting gives 18, and the mirror class also gives 18.
- {3E,1W,3N,1S}: I counted by position (ruling out adjacent E–W and N–S pairs and the four-letter blocks), giving 76. I checked this independently by splitting on the four vertical patterns (32 + 6 + 6 + 32 = 76).
- N₂ = 18 + 76 + 18 = **112**.

**Endpoint (1,1).** The classes are {4E,3W,1N} (mirror doubled) and {3E,2W,2N,1S} (mirror doubled).
- {4E,3W,1N}: the E's and W's must sit in separate rows, giving 2.
- {3E,2W,2N,1S}: splitting by the position of the S gives 18 (N,N,S), 18 (S,N,N), and 0 (N,S,N), total 36.
- N₁ = 2·(2 + 36) = **76**.

**Total.** 2·(76 + 112 + 120 + 70) = 2·378 = 756.

ANSWER: 756