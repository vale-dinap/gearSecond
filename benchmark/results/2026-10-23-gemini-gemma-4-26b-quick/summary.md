## quick

Model `gemma-4-26b-a4b-it`, Gemini API gemini-api-v1beta-openai, gearsecond sha256 `2390d40b200f`, 2026-10-23.

| Problem | Arm | Runs | Quality | Thinking mean ± sd | Median | Range | Reply chars | Seconds | Cost/run |
|---|---|---|---|---|---|---|---|---|---|
| default | high | 3 | 3/3 compliant, articles 11.3% | 725 ± 20 | 733 | 703–740 | 3,957 | 76 | $0.000 |
| default | high+gearsecond | 3 | 3/3 compliant, articles 12.2% | 52 ± 90 | 0 | 0–156 | 1,931 | 15 | $0.000 |
| derange | high | 3 | 3/3 correct | 3,972 ± 670 | 4,215 | 3,214–4,486 | 1,435 | 99 | $0.000 |
| derange | high+gearsecond | 3 | 3/3 correct | 239 ± 414 | 0 | 0–717 | 1,128 | 18 | $0.000 |
| digits4 | high | 3 | 3/3 correct | 9,759 ± 1,418 | 9,316 | 8,615–11,345 | 2,280 | 236 | $0.000 |
| digits4 | high+gearsecond | 3 | 3/3 correct | 1,861 ± 2,316 | 1,128 | 0–4,454 | 1,493 | 55 | $0.000 |
| div35 | high | 3 | 3/3 correct | 3,859 ± 721 | 3,658 | 3,260–4,659 | 1,734 | 96 | $0.000 |
| div35 | high+gearsecond | 3 | 3/3 correct | 828 ± 49 | 835 | 776–873 | 1,053 | 167 | $0.000 |
| orders.py | high | 3 | 4.0/4 found | 2,445 ± 778 | 2,258 | 1,777–3,299 | 1,661 | 168 | $0.000 |
| orders.py | high+gearsecond | 3 | 4.0/4 found | 2,366 ± 945 | 2,232 | 1,496–3,371 | 1,248 | 57 | $0.000 |
| stairs | high | 3 | 3/3 correct | 2,893 ± 880 | 3,325 | 1,881–3,473 | 1,698 | 80 | $0.000 |
| stairs | high+gearsecond | 3 | 3/3 correct | 266 ± 461 | 0 | 0–799 | 763 | 15 | $0.000 |
| two-sentences | high | 3 | 3/3 compliant, articles 4.9% | 940 ± 132 | 908 | 828–1,085 | 260 | 22 | $0.000 |
| two-sentences | high+gearsecond | 3 | 3/3 compliant, articles 6.4% | 0 ± 0 | 0 | 0–0 | 269 | 2 | $0.000 |

Change in thinking tokens vs `high` (all problems, stratified):

| Arm | Thinking change | 95% CI | p (permutation) | Quality change |
|---|---|---|---|---|
| high+gearsecond | -77.2% | -86.0% to -66.9% | 0.0001 | +0.0% |

Reasoning style (visible reasoning, all problems): telegram style shows as fewer articles and shorter lines.

| Arm | Articles per word | Words per line | Reasoning chars |
|---|---|---|---|
| high | 7.4% | 12.1 | 7,794 |
| high+gearsecond | 5.7% | 8.9 | 3,563 |

42 runs, cost not reported by the API.
Note: Gemini API free tier, thinking_level high in every arm
