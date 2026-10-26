# GearSecond

**Pump up the reasoning: a skill that gears your model up to jet-think.** Faster answers, fewer thinking tokens, lower cost, with the same model at the same effort level and the same quality.

GearSecond changes how a model thinks, not how it answers. Thinking becomes short bursts of key inferences: no full sentences, no filler, no self-talk, one check and then stop. The reply keeps whatever style it would have had anyway, including any style you, your project or another skill asked for.

Thinking without the skill:

>
> Okay, so the tests pass for the normal case. But wait, I should check `paginate`, because
> it computes the page count as `total / per_page`, which rounds down, so when total isn't a
> multiple of per_page the last partial page gets dropped. Actually, what happens when total
> is 0?
>

With it:

```
tests ok    
paginate: pages = total / per_page rounds down, so last partial page lost    
fix: pages = (total + per_page - 1) / per_page    
? total = 0: 0 pages, ok
```

## Install

Claude Code:

```
/plugin marketplace add vale-dinap/gearsecond    
/plugin install gearsecond@gearsecond
```

Then say `/gearsecond` or "gear second". It stays on until you say "stop gearsecond".

Other ways to use it:

- **claude.ai:** download `gearsecond.zip` from the latest release and upload it under Settings → Capabilities → Skills.
- **Any agent or API:** the skill is plain text. Append the body of [`SKILL.md`](plugins/gearsecond/skills/gearsecond/SKILL.md) (everything after the frontmatter) to the system prompt. That's also how the benchmark delivers it. If your model pays little attention to the system prompt (some local models do), put it at the top of your first message instead.

## Benchmark results

**TL;DR:** in tests the skill cut thinking by 16% to 77% and answered up to twice as fast.
Bugs found and maths answers held on Claude and Grok; in code review, two of the open models,
gpt-oss 20B and Qwen3.6 35B-A3B, found on average under one bug fewer out of eight. The details follow; for the takeaway, skip to
[When it helps](#when-it-helps-and-when-it-doesnt).

Same model, same effort level, with and without the skill. Thinking tokens are the counts the provider bills, not estimates. Each row compares means over repeated runs, with a 95% bootstrap interval and a permutation test.

### Code review: a 290-line Rust module with 8 planted bugs


| Model                  | Runs per arm | Bugs found    | Thinking   | Time            | Cost per review   |
|------------------------|--------------|---------------|------------|-----------------|-------------------|
| Claude Opus 5.5, high  | 10           | 8/8 → 8/8   | **−35%** | 43 s → 38 s   | $0.145 → $0.135 |
| Claude Haiku 5.5, high | 30           | 8/8 → 8/8   | **−55%** | 57 s → 31 s   | $0.008 → $0.005 |
| Grok 4.7, high         | 10           | 7.2/8 → 8/8 | **−35%** | 538 s → 361 s | $0.105 → $0.068 |


### Hard maths: 3 self-avoiding-walk counting problems, exact answers


| Model                  | Runs per arm | Correct         | Thinking (95% CI, p)                     | Time                | Cost per problem  |
|------------------------|--------------|-----------------|------------------------------------------|---------------------|-------------------|
| Claude Haiku 5.5, high | 15           | 15/15 → 15/15 | **−27%** (−40% to −12%, p = 0.005) | 394 s → 313 s     | $0.048 → $0.036 |
| Grok 4.7, high         | 15           | 12/15 → 15/15 | **−16%** (−25% to −6%, p = 0.008)  | 2,957 s → 2,534 s | $0.271 → $0.219 |


### Reply style is kept

Four prompts: no style request, "at most two sentences", "exactly 3 numbered points", and a compact style set in the system prompt (no articles, filler or pleasantries). The skill is placed *after* the style request, the position where it would be most likely to override it.


| Model                      | Default style   | Two sentences   | 3 points        | Ultra-compact      |
|----------------------------|-----------------|-----------------|-----------------|--------------------|
| Claude Opus 5.5 (3 runs)   | 3/3 → 3/3     | 1/3 → 3/3     | 3/3 → 3/3     | 3/3 → 3/3        |
| Claude Haiku 5.5 (10 runs) | 10/10 → 10/10 | 10/10 → 10/10 | 10/10 → 10/10 | 10/10 → **6/10** |
| Grok 4.7 (10 runs)         | 10/10 → 10/10 | 10/10 → 10/10 | 10/10 → 10/10 | 0/10 → 0/10      |


Grok CLI's own reply guidelines override styles set in the system prompt, with or without the skill, hence 0/10 in both arms.

### Open models

The quick mix is four exact-answer maths problems, a Python bug hunt and two reply styles.

| Model                         | Task        | Runs per arm | Quality                                | Thinking   | Time          |
|-------------------------------|-------------|--------------|----------------------------------------|------------|---------------|
| Gemma 4 26B-A4B, thinking on  | Code review | 8            | 6.6/8 → 6.5/8 bugs                     | **−55%** | 115 s → 61 s  |
| Gemma 4 26B-A4B, thinking on  | Quick mix   | 3            | maths, bugs, styles: all kept          | **−77%** |               |
| Qwen3.6 35B-A3B               | Code review | 8 / 16       | 6.0/8 → 5.8/8 bugs                     | **−19%** | 692 s → 511 s |
| Qwen3.6 35B-A3B               | Quick mix   | 5            | maths 20/20, bugs 4/4, styles 10 → 9/10 | **−42%** |               |
| gpt-oss 20B, medium           | Code review | 20           | 6.2/8 → 5.4/8 bugs                     | **−34%** | 268 s → 170 s |
| gpt-oss 20B, medium           | Quick mix   | 5            | maths 19/20 → 20/20, bugs 4/4, styles 10 → 9/10 | **−50%** |               |

With the skill on, Gemma often skips thinking altogether, and those runs found as many bugs
as the rest: the skill seems to help it recognise when a task needs no thinking at all. On the
smaller models, the code review found on average under one bug fewer out of eight. Qwen's
code review ran 8 times without the skill and 16 with it.

Every table, the exact prompts and every raw response are in [`benchmark/results`](benchmark/results/README.md), and the whole benchmark reruns with one command. See [`benchmark/README.md`](benchmark/README.md).

## When it helps, and when it doesn't

- **Reasoning-heavy work** (reviews, debugging, maths, planning) is where it pays: thinking is most of the output there, and it's what the skill shortens.
- **Short prompts** cost slightly more. The skill adds about 1,000 input tokens, and a one-line question has little thinking to save.
- **The effort level is still the biggest lever.** GearSecond makes each effort level cheaper and quicker; it doesn't replace choosing a lower one when a task is easy.

## Known limitations

- **Small models and conflicting style rules:** Haiku kept the compact reply style in only 6 of 10 runs with the skill on, against 10 of 10 without. Larger models kept it. This affects only the reply's wording, not the savings or the answers: on Haiku the skill still cut thinking by 55% on code review and 27% on maths, with nothing missed.
- **The effect varies by model.** It depends on how compact a model's own reasoning already is: a model that already thinks tersely has less to compress. A few models may occasionally also apply some of the skill rules to their replies, and answer more briefly.

## License

[Apache-2.0](LICENSE) © Valerio Di Napoli

 
