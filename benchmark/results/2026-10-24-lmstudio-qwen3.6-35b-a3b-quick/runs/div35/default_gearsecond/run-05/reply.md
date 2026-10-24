Let A = multiples of 3 in [1, 1000].
Let B = multiples of 5 in [1, 1000].
Condition: elements in A ∪ B but not in A ∩ B.
A ∩ B = multiples of lcm(3, 5) = 15.
|A| = ⌊1000/3⌋ = 333.
|B| = ⌊1000/5⌋ = 200.
|A ∩ B| = ⌊1000/15⌋ = 66.
|A ∪ B| = |A| + |B| - |A ∩ B| = 333 + 200 - 66 = 467.
Subtract those divisible by 15: 467 - 66 = 401.
Cross-check via disjoint sets: (divisible by 3 only) + (divisible by 5 only) = (333 - 66) + (200 - 66) = 267 + 134 = 401.
ANSWER: 401