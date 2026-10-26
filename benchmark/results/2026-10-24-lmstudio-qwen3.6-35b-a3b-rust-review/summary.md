## rust-review

Model `qwen/qwen3.6-35b-a3b`, LM Studio lms-commit-dcefd5a, gearsecond sha256 `2390d40b200f`, 2026-10-24.

| Problem | Arm | Runs | Quality | Thinking mean ± sd | Median | Range | Reply chars | Seconds | Cost/run |
|---|---|---|---|---|---|---|---|---|---|
| lib.rs | default | 8 | 6.0/8 found, 2 hit budget | 7,220 ± 850 | 7,244 | 5,526–8,204 | 3,588 | 692 | $0.000 |
| lib.rs | default+gearsecond | 16 | 5.8/8 found, 2 hit budget | 5,828 ± 1,181 | 5,636 | 3,824–8,204 | 2,068 | 511 | $0.000 |

Change in thinking tokens vs `default`:

| Arm | Thinking change | 95% CI | p (permutation) | Quality change |
|---|---|---|---|---|
| default+gearsecond | -19.3% | -28.2% to -8.8% | 0.0068 | -2.3% |

Reasoning style (visible reasoning, all problems): telegram style shows as fewer articles and shorter lines.

| Arm | Articles per word | Words per line | Reasoning chars |
|---|---|---|---|
| default | 3.8% | 11.7 | 23,417 |
| default+gearsecond | 2.1% | 10.2 | 17,797 |

24 runs, no API cost (local model).
Reasoning budget: 8192 tokens.
Note: context 65536, Enable thinking on, reasoning budget 8192 with message '... wait, that's enough. I have to answer now.', LM Studio default sampling
