## rust-review

Model `openai/gpt-oss-20b`, LM Studio lms-commit-dcefd5a, gearsecond sha256 `2390d40b200f`, 2026-10-23.

| Problem | Arm | Runs | Quality | Thinking mean ± sd | Median | Range | Reply chars | Seconds | Cost/run |
|---|---|---|---|---|---|---|---|---|---|
| lib.rs | medium | 20 | 6.2/8 found | 3,709 ± 1,919 | 3,190 | 1,843–10,165 | 3,388 | 268 | $0.000 |
| lib.rs | medium+gearsecond | 20 | 5.4/8 found | 2,466 ± 1,161 | 1,959 | 1,462–5,758 | 2,103 | 170 | $0.000 |

Change in thinking tokens vs `medium`:

| Arm | Thinking change | 95% CI | p (permutation) | Quality change |
|---|---|---|---|---|
| medium+gearsecond | -33.5% | -50.2% to -10.5% | 0.0108 | -10.6% |

Reasoning style (visible reasoning, all problems): telegram style shows as fewer articles and shorter lines.

| Arm | Articles per word | Words per line | Reasoning chars |
|---|---|---|---|
| medium | 1.2% | 19.5 | 15,934 |
| medium+gearsecond | 0.9% | 20.7 | 10,814 |

40 runs, no API cost (local model).
Note: context 65k, reasoning_effort medium (sent per request), no reasoning budget, LM Studio default sampling
