## rust-review

Model `grok-4.7` (served as `grok-4.7-build`), Grok CLI 1.0.67, gearsecond sha256 `2390d40b200f`, 2026-10-22.

| Problem | Arm | Runs | Quality | Thinking mean ± sd | Median | Range | Reply chars | Seconds | Cost/run |
|---|---|---|---|---|---|---|---|---|---|
| lib.rs | high | 10 | 7.2/8 found | 34,656 ± 7,927 | 33,355 | 21,716–48,902 | 6,634 | 538 | $0.105 |
| lib.rs | high+gearsecond | 10 | 8.0/8 found | 22,440 ± 5,583 | 22,272 | 14,927–29,522 | 5,613 | 361 | $0.068 |

Change in thinking tokens vs `high`:

| Arm | Thinking change | 95% CI | p (permutation) | Quality change |
|---|---|---|---|---|
| high+gearsecond | -35.2% | -47.4% to -21.7% | 0.0011 | +10.0% |

20 runs, total cost $1.73 at list API prices.
