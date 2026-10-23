## style

Model `claude-opus-5-5`, Claude Code 2.1.308, gearsecond sha256 `2390d40b200f`, 2026-10-22.

| Problem | Arm | Runs | Quality | Thinking mean ± sd | Median | Range | Reply chars | Seconds | Cost/run |
|---|---|---|---|---|---|---|---|---|---|
| compact | high | 3 | 3/3 compliant, articles 0.0% | 0 ± 0 | 0 | 0–0 | 719 | 4 | $0.025 |
| compact | high+gearsecond | 3 | 3/3 compliant, articles 0.0% | 0 ± 0 | 0 | 0–0 | 545 | 3 | $0.035 |
| default | high | 3 | 3/3 compliant, articles 9.8% | 21 ± 1 | 22 | 20–22 | 3,666 | 16 | $0.044 |
| default | high+gearsecond | 3 | 3/3 compliant, articles 8.5% | 0 ± 0 | 0 | 0–0 | 3,897 | 17 | $0.058 |
| numbered-3 | high | 3 | 3/3 compliant, articles 12.5% | 0 ± 0 | 0 | 0–0 | 439 | 3 | $0.022 |
| numbered-3 | high+gearsecond | 3 | 3/3 compliant, articles 10.9% | 0 ± 0 | 0 | 0–0 | 489 | 3 | $0.034 |
| two-sentences | high | 3 | 1/3 compliant, articles 6.4% | 0 ± 0 | 0 | 0–0 | 438 | 3 | $0.021 |
| two-sentences | high+gearsecond | 3 | 3/3 compliant, articles 6.3% | 14 ± 8 | 9 | 9–23 | 431 | 3 | $0.035 |

Change in thinking tokens vs `high` (all problems, stratified):

| Arm | Thinking change | 95% CI | p (permutation) | Quality change |
|---|---|---|---|---|
| high+gearsecond | -35.9% | -59.1% to +4.5% | 0.5512 | +16.7% |

24 runs, total cost $0.82 at list API prices.
Note: Run while the skill was still a draft under another name; its text is byte-identical to the shipped SKILL.md body (same sha256). Arms for other drafts were removed from this published copy.
