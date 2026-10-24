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
| `2026-10-24-gemini-gemma-4-26b-rust-review` | Gemma 4 26B, thinking on (Gemini API) | Code review | Open models, Gemma |
| `2026-10-23-gemini-gemma-4-26b-quick` | Gemma 4 26B, thinking on (Gemini API) | Quick mix | Open models, Gemma |
| `2026-10-24-lmstudio-qwen3.6-35b-a3b-rust-review` | Qwen 3.6 35B (LM Studio) | Code review | Open models, Qwen |
| `2026-10-24-lmstudio-qwen3.6-35b-a3b-quick` | Qwen 3.6 35B (LM Studio) | Quick mix | Open models, Qwen |
| `2026-10-23-lmstudio-gpt-oss-20b-medium-rust-review` | gpt-oss-20b, medium (LM Studio) | Code review | Open models, gpt-oss |
| `2026-10-23-lmstudio-gpt-oss-20b-medium-quick` | gpt-oss-20b, medium (LM Studio) | Quick mix | Open models, gpt-oss |

Local models' settings (context, reasoning budget) are in each manifest's `note`.

Rebuild any table with `python summarize.py results/<folder>`. Summaries rescore the
replies with the current scorers, so they can differ slightly from a `summary.md` written
before a scorer fix.
