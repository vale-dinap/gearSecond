## style

Model `grok-4.7` (served as `grok-4.7-build`), Grok CLI 1.0.67, gearsecond sha256 `2390d40b200f`, 2026-10-22.

| Problem | Arm | Runs | Quality | Thinking mean ± sd | Median | Range | Reply chars | Seconds | Cost/run |
|---|---|---|---|---|---|---|---|---|---|
| compact | high | 10 | 0/10 compliant, articles 7.0% | 247 ± 103 | 246 | 118–466 | 511 | 7 | $0.009 |
| compact | high+gearsecond | 10 | 0/10 compliant, articles 9.0% | 200 ± 76 | 194 | 100–359 | 540 | 6 | $0.010 |
| default | high | 10 | 10/10 compliant, articles 10.8% | 770 ± 225 | 772 | 494–1,226 | 2,246 | 24 | $0.010 |
| default | high+gearsecond | 10 | 10/10 compliant, articles 10.0% | 499 ± 161 | 462 | 326–800 | 1,868 | 19 | $0.009 |
| numbered-3 | high | 10 | 10/10 compliant, articles 11.8% | 498 ± 86 | 502 | 378–653 | 394 | 10 | $0.009 |
| numbered-3 | high+gearsecond | 10 | 10/10 compliant, articles 13.3% | 504 ± 73 | 498 | 388–590 | 379 | 11 | $0.008 |
| two-sentences | high | 10 | 10/10 compliant, articles 6.5% | 797 ± 278 | 708 | 498–1,367 | 297 | 17 | $0.009 |
| two-sentences | high+gearsecond | 10 | 10/10 compliant, articles 6.0% | 644 ± 194 | 609 | 376–919 | 262 | 14 | $0.008 |

Change in thinking tokens vs `high` (all problems, stratified):

| Arm | Thinking change | 95% CI | p (permutation) | Quality change |
|---|---|---|---|---|
| high+gearsecond | -20.1% | -29.9% to -9.1% | 0.0041 | +0.0% |

80 runs, total cost $0.73 at list API prices.
