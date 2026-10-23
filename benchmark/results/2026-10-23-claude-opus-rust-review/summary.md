## rust-review

Model `claude-opus-5-5`, Claude Code 2.1.308, gearsecond sha256 `2390d40b200f`, 2026-10-22.

| Problem | Arm | Runs | Quality | Thinking mean ± sd | Median | Range | Reply chars | Seconds | Cost/run |
|---|---|---|---|---|---|---|---|---|---|
| lib.rs | high | 10 | 8.0/8 found | 1,343 ± 343 | 1,252 | 1,021–2,045 | 5,557 | 43 | $0.145 |
| lib.rs | high+gearsecond | 10 | 8.0/8 found | 877 ± 101 | 857 | 762–1,050 | 5,086 | 38 | $0.135 |

Change in thinking tokens vs `high`:

| Arm | Thinking change | 95% CI | p (permutation) | Quality change |
|---|---|---|---|---|
| high+gearsecond | -34.7% | -44.7% to -23.5% | 0.0001 | +0.0% |

20 runs, total cost $2.81 at list API prices.
Note: Run while the skill was still a draft under another name; its text is byte-identical to the shipped SKILL.md body (same sha256). Arms for other drafts were removed from this published copy.
