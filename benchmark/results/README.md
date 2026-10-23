# Results

Each folder is one benchmark run of the shipped skill (sha256 `2390d40b200f`) against the
same model without it. It holds the manifest, the exact skill text, every raw response and
a `summary.md`.

| Folder | Model | Task | Main README row |
|---|---|---|---|
| `2026-10-23-claude-opus-rust-review` | Claude Opus 5.5 | Code review | Code review, Opus |
| `2026-10-22-claude-haiku-rust-review` | Claude Haiku 5.5 | Code review | Code review, Haiku |
| `2026-10-23-grok-rust-review` | Grok 4.7 | Code review | Code review, Grok |
| `2026-10-22-claude-haiku-counting` | Claude Haiku 5.5 | Hard maths | Hard maths, Haiku |
| `2026-10-23-grok-counting` | Grok 4.7 | Hard maths | Hard maths, Grok (29 of 30 runs) |
| `2026-10-23-claude-opus-style` | Claude Opus 5.5 | Reply style | Reply style, Opus |
| `2026-10-23-claude-haiku-style` | Claude Haiku 5.5 | Reply style | Reply style, Haiku |
| `2026-10-23-grok-style` | Grok 4.7 | Reply style | Reply style, Grok |
| `2026-10-23-lmstudio-gpt-oss-20b-low` | gpt-oss-20b, low reasoning | Quick mix | Exploratory: 1 run per arm |
| `2026-10-23-lmstudio-gpt-oss-20b-high-rust-review` | gpt-oss-20b, high reasoning | Code review | In progress |
| `2026-10-23-gemini-api-gemma-4-26b-*` | Gemma 4 26B (Gemini API) | Review, style, quick mix | In progress |

Rebuild any table with `python summarize.py results/<folder>`. Summaries rescore the
replies with the current scorers, so they can differ slightly from a `summary.md` written
before a scorer fix.
