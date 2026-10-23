## counting

Model `grok-4.7` (served as `grok-4.7-build`), Grok CLI 1.0.67, gearsecond sha256 `2390d40b200f`, 2026-10-22.

| Problem | Arm | Runs | Quality | Thinking mean ± sd | Median | Range | Reply chars | Seconds | Cost/run |
|---|---|---|---|---|---|---|---|---|---|
| saw | high | 5 | 4/5 correct | 110,124 ± 23,098 | 108,832 | 75,374–139,234 | 1,872 | 1984 | $0.253 |
| saw | high+gearsecond | 5 | 5/5 correct | 94,947 ± 18,376 | 91,228 | 77,283–124,412 | 1,630 | 2213 | $0.205 |
| saw_diag | high | 5 | 5/5 correct | 112,963 ± 14,981 | 112,273 | 93,327–131,538 | 1,454 | 2862 | $0.238 |
| saw_diag | high+gearsecond | 5 | 5/5 correct | 91,025 ± 5,142 | 93,006 | 84,192–96,340 | 2,032 | 2181 | $0.197 |
| saw_quad | high | 4 | 3/4 correct | 139,884 ± 22,441 | 131,624 | 123,274–173,015 | 1,796 | 4024 | $0.323 |
| saw_quad | high+gearsecond | 5 | 5/5 correct | 119,947 ± 23,119 | 114,429 | 87,451–146,853 | 1,393 | 3208 | $0.254 |

Change in thinking tokens vs `high` (all problems, stratified):

| Arm | Thinking change | 95% CI | p (permutation) | Quality change |
|---|---|---|---|---|
| high+gearsecond | -15.7% | -24.6% to -5.9% | 0.0083 | +14.3% |

29 runs, total cost $7.03 at list API prices.
