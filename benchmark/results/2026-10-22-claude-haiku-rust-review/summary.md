## rust-review

Model `claude-haiku-5-5`, Claude Code 2.1.308, gearsecond sha256 `2390d40b200f`, 2026-10-22.

| Problem | Arm | Runs | Quality | Thinking mean ± sd | Median | Range | Reply chars | Seconds | Cost/run |
|---|---|---|---|---|---|---|---|---|---|
| lib.rs | high | 30 | 8.0/8 found | 10,232 ± 1,880 | 10,054 | 7,136–14,461 | 5,711 | 57 | $0.008 |
| lib.rs | high+gearsecond | 30 | 8.0/8 found | 4,603 ± 1,253 | 4,420 | 3,043–8,916 | 4,702 | 31 | $0.005 |

Change in thinking tokens vs `high`:

| Arm | Thinking change | 95% CI | p (permutation) | Quality change |
|---|---|---|---|---|
| high+gearsecond | -55.0% | -59.8% to -49.3% | 0.0001 | +0.0% |

60 runs, total cost $0.40 at list API prices.
Note: Run while the skill was still a draft under another name; its text is byte-identical to the shipped SKILL.md body (same sha256). Arms for other drafts were removed from this published copy.
