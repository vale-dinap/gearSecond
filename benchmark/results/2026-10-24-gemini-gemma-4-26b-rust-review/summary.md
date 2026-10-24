## rust-review

Model `gemma-4-26b-a4b-it`, Gemini API gemini-api-v1beta-openai, gearsecond sha256 `2390d40b200f`, 2026-10-24.

| Problem | Arm | Runs | Quality | Thinking mean ± sd | Median | Range | Reply chars | Seconds | Cost/run |
|---|---|---|---|---|---|---|---|---|---|
| lib.rs | high | 8 | 6.6/8 found | 4,549 ± 887 | 4,338 | 3,270–6,240 | 3,198 | 115 | $0.000 |
| lib.rs | high+gearsecond | 8 | 6.5/8 found | 2,070 ± 2,244 | 1,820 | 0–4,790 | 2,728 | 61 | $0.000 |

Change in thinking tokens vs `high`:

| Arm | Thinking change | 95% CI | p (permutation) | Quality change |
|---|---|---|---|---|
| high+gearsecond | -54.5% | -87.5% to -20.3% | 0.0188 | -1.6% |

Reasoning style (visible reasoning, all problems): telegram style shows as fewer articles and shorter lines.

| Arm | Articles per word | Words per line | Reasoning chars |
|---|---|---|---|
| high | 4.3% | 9.4 | 13,432 |
| high+gearsecond | 1.9% | 8.5 | 11,382 |

16 runs, cost not reported by the API.
Note: Gemini API free tier, thinking_level high in every arm
