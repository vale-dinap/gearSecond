**Answer: 756**

An 8-step walk from the origin can't end at the origin, and it can only reach (a,a) if 2|a| ≤ 8. So the endpoints are (±a, ±a) with a = 1,…,4. Point reflection maps walks to (a,a) bijectively onto walks to (−a,−a), so the total is 2·Σₐ N(a,a), where N(a,a) counts 8-step SAWs from the origin to (a,a).

**Method.** A walk's revisit is a contiguous block of steps with zero net displacement. For each step-count type I used the same decomposition: each maximal horizontal run within one visit to a row must be monotone, and visits to the same row must occupy disjoint x-intervals. I cross-checked several counts with a second method (closed contiguous blocks, or the visit decomposition).

- **N(4,4) = 70.** All 8 steps must be 4 E and 4 N, so every C(8,4) ordering works.
- **N(3,3) = 120.** The step types are {4E, 1W, 3N} or its diagonal mirror {3E, 4N, 1S}. Each has 60 walks: 4 E's and 3 N's with one W placed where it has no E neighbour (the visit decomposition gives the same 60).
- **N(2,2) = 112.** The step types are {4E, 2W, 2N} (18 walks), its mirror {2E, 4N, 2S} (18), and {3E, 1W, 3N, 1S} (76). Total 18 + 18 + 76 = 112.
- **N(1,1) = 76.** The step types are {4E, 3W, 1N} (2 walks), its mirror {1E, 3N, 4S} (2), {3E, 2W, 2N, 1S} (36), and its mirror {1E, 2W, 3N, 2S} (36). Total 2 + 2 + 36 + 36 = 76. The 36 is 18 + 0 + 18 over the three vertical patterns NNS, NSN, SNN; NNS and SNN are related by time reversal, and NSN gives 0.

**Total:**

2 · (N(1,1) + N(2,2) + N(3,3) + N(4,4)) = 2 · (76 + 112 + 120 + 70) = 2 · 378 = 756

ANSWER: 756