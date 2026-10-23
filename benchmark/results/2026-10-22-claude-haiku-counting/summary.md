## counting

Model `claude-haiku-5-5`, Claude Code 2.1.308, gearsecond sha256 `2390d40b200f`, 2026-10-22.

| Problem | Arm | Runs | Quality | Thinking mean ± sd | Median | Range | Reply chars | Seconds | Cost/run |
|---|---|---|---|---|---|---|---|---|---|
| saw | high | 5 | 5/5 correct | 82,849 ± 4,642 | 82,143 | 78,145–90,581 | 1,506 | 360 | $0.042 |
| saw | high+gearsecond | 5 | 5/5 correct | 74,861 ± 21,016 | 70,284 | 56,634–111,075 | 1,045 | 374 | $0.039 |
| saw_diag | high | 5 | 5/5 correct | 118,788 ± 55,440 | 95,132 | 74,983–214,718 | 1,611 | 487 | $0.060 |
| saw_diag | high+gearsecond | 5 | 5/5 correct | 70,461 ± 10,056 | 74,402 | 59,718–82,870 | 1,353 | 302 | $0.036 |
| saw_quad | high | 5 | 5/5 correct | 80,661 ± 20,853 | 91,997 | 57,079–98,312 | 1,669 | 335 | $0.041 |
| saw_quad | high+gearsecond | 5 | 5/5 correct | 61,537 ± 14,239 | 55,024 | 47,722–84,248 | 1,120 | 263 | $0.032 |

Change in thinking tokens vs `high` (all problems, stratified):

| Arm | Thinking change | 95% CI | p (permutation) | Quality change |
|---|---|---|---|---|
| high+gearsecond | -26.7% | -40.0% to -11.8% | 0.0050 | +0.0% |

30 runs, total cost $1.26 at list API prices.
Note: Run while the skill was still a draft under another name; its text is byte-identical to the shipped SKILL.md body (same sha256). Arms for other drafts were removed from this published copy.
