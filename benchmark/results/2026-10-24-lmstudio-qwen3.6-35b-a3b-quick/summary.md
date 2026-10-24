## quick

Model `qwen/qwen3.6-35b-a3b`, LM Studio lms-commit-dcefd5a, gearsecond sha256 `2390d40b200f`, 2026-10-24.

| Problem | Arm | Runs | Quality | Thinking mean ± sd | Median | Range | Reply chars | Seconds | Cost/run |
|---|---|---|---|---|---|---|---|---|---|
| default | default | 5 | 5/5 compliant, articles 5.5%, 0 hit budget | 1,304 ± 130 | 1,306 | 1,134–1,499 | 4,048 | 149 | $0.000 |
| default | default+gearsecond | 5 | 4/5 compliant, articles 5.2%, 0 hit budget | 1,109 ± 150 | 1,021 | 1,016–1,362 | 1,134 | 97 | $0.000 |
| derange | default | 5 | 5/5 correct, 1 hit budget | 5,634 ± 2,560 | 6,301 | 2,320–8,205 | 2,111 | 446 | $0.000 |
| derange | default+gearsecond | 5 | 5/5 correct, 0 hit budget | 1,284 ± 260 | 1,325 | 932–1,539 | 537 | 110 | $0.000 |
| digits4 | default | 5 | 5/5 correct, 5 hit budget | 8,205 ± 0 | 8,205 | 8,205–8,205 | 1,890 | 631 | $0.000 |
| digits4 | default+gearsecond | 5 | 5/5 correct, 2 hit budget | 5,434 ± 2,973 | 6,304 | 1,900–8,205 | 1,040 | 429 | $0.000 |
| div35 | default | 5 | 5/5 correct, 0 hit budget | 5,654 ± 1,888 | 5,606 | 3,252–7,542 | 2,074 | 440 | $0.000 |
| div35 | default+gearsecond | 5 | 5/5 correct, 0 hit budget | 3,437 ± 1,819 | 3,565 | 1,665–6,151 | 625 | 263 | $0.000 |
| orders.py | default | 5 | 4.0/4 found, 0 hit budget | 3,804 ± 212 | 3,670 | 3,648–4,135 | 2,043 | 294 | $0.000 |
| orders.py | default+gearsecond | 5 | 4.0/4 found, 0 hit budget | 3,547 ± 2,273 | 2,617 | 2,302–7,597 | 1,280 | 279 | $0.000 |
| stairs | default | 5 | 5/5 correct, 1 hit budget | 3,460 ± 2,689 | 2,501 | 1,778–8,205 | 1,347 | 277 | $0.000 |
| stairs | default+gearsecond | 5 | 5/5 correct, 0 hit budget | 1,443 ± 696 | 1,598 | 631–2,212 | 452 | 120 | $0.000 |
| two-sentences | default | 5 | 5/5 compliant, articles 3.6%, 0 hit budget | 1,708 ± 1,250 | 1,139 | 507–3,702 | 266 | 117 | $0.000 |
| two-sentences | default+gearsecond | 5 | 5/5 compliant, articles 2.5%, 0 hit budget | 931 ± 216 | 1,004 | 678–1,207 | 206 | 69 | $0.000 |

Change in thinking tokens vs `default` (all problems, stratified):

| Arm | Thinking change | 95% CI | p (permutation) | Quality change |
|---|---|---|---|---|
| default+gearsecond | -42.3% | -54.4% to -28.6% | 0.0001 | -2.9% |

Reasoning style (visible reasoning, all problems): telegram style shows as fewer articles and shorter lines.

| Arm | Articles per word | Words per line | Reasoning chars |
|---|---|---|---|
| default | 6.1% | 11.0 | 11,800 |
| default+gearsecond | 5.2% | 9.1 | 6,493 |

70 runs, no API cost (local model).
Reasoning budget: 8192 tokens.
Note: context 65536, Enable thinking on, reasoning budget 8192 with message '... wait, that's enough. I have to answer now.', LM Studio default sampling
