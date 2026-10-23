There are **756** such walks. I counted by hand, splitting each endpoint's walks by step multiset and checking the results with symmetry.

**Setup.** Endpoints on y = x after 8 steps are (k,k) with k = ±1, ±2, ±3, ±4. The point reflection through the origin maps (k,k) to (−k,−k), so the total is 2(N₁ + N₂ + N₃ + N₄), where Nₖ is the count ending at (k,k).

**N₄ = 70.** Reaching (4,4) in 8 steps forces only N and E steps, giving C(8,4) = 70.

**N₃ = 120.** Two step multisets are possible: {E³,N⁴,S¹} and {E⁴,N³,W¹}. Reflection in y = x swaps them, so each contributes 60. For {E³,N⁴,S¹}, the S step must be isolated from every N in the walk, and counting the valid arrangements gives 60.

**N₂ = 112.** Multisets: {E²,N⁴,S²}, its mirror {N²,E⁴,W²} (18 each), and the self-symmetric {E³,W¹,N³,S¹} (76). The 18 comes from counting arrangements where each maximal vertical run lies in one column (two methods agree). The 76 splits by where the W sits among the horizontal steps: WEEE = 32, EEEW = 32, EWEE = 6, EEWE = 6. Reversing a walk and mapping it through (x,y) ↦ (2,2) − (x,y) pairs the WEEE/EEEW and EWEE/EEWE cases, and each pair was counted independently and agreed.

**N₁ = 76.** Multisets: {E¹,N⁴,S³} (2 walks), its mirror {N¹,E⁴,W³} (2), {E²,W¹,N³,S²} (36), and its mirror {E³,W²,N²,S¹} (36). For the 36, the W orders EEW and WEE give 18 each (reversal-paired), and EWE gives 0. The 2 walks in {E¹,N⁴,S³} are NNNNESSS and SSSENNNN.

**Total:** 2 × (76 + 112 + 120 + 70) = 2 × 378 = 756.

ANSWER: 756