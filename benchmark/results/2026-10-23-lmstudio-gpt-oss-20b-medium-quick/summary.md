## quick

Model `openai/gpt-oss-20b`, LM Studio lms-commit-dcefd5a, gearsecond sha256 `2390d40b200f`, 2026-10-23.

| Problem | Arm | Runs | Quality | Thinking mean ± sd | Median | Range | Reply chars | Seconds | Cost/run |
|---|---|---|---|---|---|---|---|---|---|
| default | medium | 5 | 5/5 compliant, articles 9.4% | 583 ± 225 | 537 | 383–941 | 4,944 | 70 | $0.000 |
| default | medium+gearsecond | 5 | 4/5 compliant, articles 7.4% | 145 ± 55 | 132 | 83–231 | 829 | 16 | $0.000 |
| derange | medium | 5 | 5/5 correct | 685 ± 188 | 738 | 490–926 | 1,293 | 48 | $0.000 |
| derange | medium+gearsecond | 5 | 5/5 correct | 313 ± 63 | 327 | 208–369 | 276 | 20 | $0.000 |
| digits4 | medium | 5 | 4/5 correct | 1,335 ± 762 | 1,036 | 820–2,681 | 1,229 | 72 | $0.000 |
| digits4 | medium+gearsecond | 5 | 5/5 correct | 405 ± 84 | 379 | 328–534 | 171 | 22 | $0.000 |
| div35 | medium | 5 | 5/5 correct | 652 ± 191 | 581 | 464–895 | 1,248 | 45 | $0.000 |
| div35 | medium+gearsecond | 5 | 5/5 correct | 430 ± 96 | 439 | 285–521 | 125 | 22 | $0.000 |
| orders.py | medium | 5 | 4.0/4 found | 1,068 ± 357 | 908 | 739–1,566 | 2,070 | 65 | $0.000 |
| orders.py | medium+gearsecond | 5 | 4.0/4 found | 892 ± 304 | 858 | 544–1,335 | 1,666 | 56 | $0.000 |
| stairs | medium | 5 | 5/5 correct | 364 ± 203 | 292 | 178–585 | 1,201 | 34 | $0.000 |
| stairs | medium+gearsecond | 5 | 5/5 correct | 262 ± 133 | 212 | 145–448 | 639 | 22 | $0.000 |
| two-sentences | medium | 5 | 5/5 compliant, articles 4.3% | 346 ± 112 | 349 | 232–490 | 362 | 18 | $0.000 |
| two-sentences | medium+gearsecond | 5 | 5/5 compliant, articles 3.9% | 93 ± 59 | 56 | 53–188 | 350 | 9 | $0.000 |

Change in thinking tokens vs `medium` (all problems, stratified):

| Arm | Thinking change | 95% CI | p (permutation) | Quality change |
|---|---|---|---|---|
| medium+gearsecond | -49.5% | -58.1% to -39.6% | 0.0001 | +0.0% |

Reasoning style (visible reasoning, all problems): telegram style shows as fewer articles and shorter lines.

| Arm | Articles per word | Words per line | Reasoning chars |
|---|---|---|---|
| medium | 3.1% | 23.4 | 2,556 |
| medium+gearsecond | 1.3% | 25.4 | 1,309 |

70 runs, no API cost (local model).
Note: context 65k, reasoning_effort medium (sent per request), no reasoning budget, LM Studio default sampling
