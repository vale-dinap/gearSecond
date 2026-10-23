## style

Model `claude-haiku-5-5`, Claude Code 2.1.308, gearsecond sha256 `2390d40b200f`, 2026-10-22.

| Problem | Arm | Runs | Quality | Thinking mean ± sd | Median | Range | Reply chars | Seconds | Cost/run |
|---|---|---|---|---|---|---|---|---|---|
| compact | high | 10 | 10/10 compliant, articles 0.9% | 98 ± 64 | 86 | 0–203 | 480 | 3 | $0.001 |
| compact | high+gearsecond | 10 | 6/10 compliant, articles 2.2% | 121 ± 57 | 111 | 58–231 | 460 | 3 | $0.001 |
| default | high | 10 | 10/10 compliant, articles 10.4% | 654 ± 271 | 532 | 337–1,189 | 3,229 | 10 | $0.001 |
| default | high+gearsecond | 10 | 10/10 compliant, articles 9.9% | 355 ± 198 | 336 | 60–757 | 2,752 | 8 | $0.002 |
| numbered-3 | high | 10 | 10/10 compliant, articles 15.8% | 0 ± 0 | 0 | 0–0 | 478 | 2 | $0.001 |
| numbered-3 | high+gearsecond | 10 | 10/10 compliant, articles 12.7% | 0 ± 0 | 0 | 0–0 | 382 | 2 | $0.001 |
| two-sentences | high | 10 | 10/10 compliant, articles 8.4% | 0 ± 0 | 0 | 0–0 | 432 | 2 | $0.001 |
| two-sentences | high+gearsecond | 10 | 10/10 compliant, articles 7.3% | 61 ± 84 | 0 | 0–198 | 365 | 2 | $0.001 |

Change in thinking tokens vs `high` (all problems, stratified):

| Arm | Thinking change | 95% CI | p (permutation) | Quality change |
|---|---|---|---|---|
| high+gearsecond | -28.4% | -48.8% to -0.8% | 0.1012 | -10.0% |

80 runs, total cost $0.08 at list API prices.
Note: Run while the skill was still a draft under another name; its text is byte-identical to the shipped SKILL.md body (same sha256). Arms for other drafts were removed from this published copy.
