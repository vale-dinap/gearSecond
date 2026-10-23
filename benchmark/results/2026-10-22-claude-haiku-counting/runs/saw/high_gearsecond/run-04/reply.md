**Answer: 522**

Walks of length 8 end at (x,0) only for even x, so I counted each endpoint and used the reflection x → −x:

| Endpoint | Walks |
|---|---|
| (±8,0) | 1 each |
| (±6,0) | 42 each |
| (±4,0) | 126 each |
| (±2,0) | 92 each |

Total = 2 × (1 + 42 + 126 + 92) = 522.

The counts come from a hand enumeration, not code. Each walk is split into horizontal segments, with vertical excursions between them, and the self-avoidance constraints are checked per column. Spot checks: the method reproduces the 6 four-step walks ending at (2,0) and the 6 three-step walks ending on the x-axis.

ANSWER: 522