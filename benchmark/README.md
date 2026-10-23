# GearSecond benchmark

Measures whether GearSecond reduces thinking tokens without lowering answer quality. Each
task runs the same prompt with and without the skill and records the exact thinking-token
count the backend reports for every run. Supported backends: Claude Code (`--cli claude`,
the default), Grok CLI (`--cli grok`), LM Studio for local models (`--cli lmstudio`) and
the Gemini API (`--cli gemini`). `clis.py` holds what differs between them. The results
and which arm in each is the shipped skill are listed in
[`results/README.md`](results/README.md).

## What is measured

- **Thinking tokens:** the reasoning tokens the provider bills, from the CLI's JSON
  output. That's `usage.output_tokens_details.thinking_tokens` for Claude Code and
  `usage.reasoning_tokens` for Grok CLI. It's never an estimate from visible text.
  - **Claude Code** doesn't show thinking text, so the benchmark can check the length of
    the thinking but not its style.
  - **Grok CLI** returns a `thought` field, but it's a summary, often about 10× shorter
    than the billed reasoning. Comparing visible reasoning across runs therefore
    understates the real token use.
- **Quality:**
  - `rust-review`: how many of the 8 planted bugs the review cites, matched by line number.
  - `style`: whether the reply keeps the style that was asked for.
  - `counting`: whether the final `ANSWER:` line is exactly right.
- **Also recorded:** reply length, duration, and cost at list API prices
  (`total_cost_usd`). Cost doesn't depend on your plan.

## Tasks

| Task | What it is | Answer key |
|---|---|---|
| `rust-review` | Review a 290-line Rust module with 8 planted bugs: underflow, overwrite instead of add, off-by-one panic, unchecked index, dangling pointer, length truncation, unchecked UTF-8, lock-order deadlock | `// @BUG:<name>` markers in `tasks/rust-review/src/lib.rs`, stripped before the model sees the code. The crate compiles and its tests pass (`cargo test`). |
| `style` | 4 prompts that request a reply style: at most two sentences, exactly 3 numbered points, a compact style (no articles, filler or pleasantries) in the system prompt, and no style at all | Checks sentence count, item count and article rate (compact: under 3% of words; normal prose: over 4%), in `bench.py`. |
| `counting` | 12 exact-answer combinatorics problems (self-avoiding walks, constrained permutations, lattice paths…) | `tasks/counting/problems.json`. Recompute it with `python tasks/counting/verify_answers.py`. |

## Reproducing

Requirements:

- Claude Code or Grok CLI, logged in.
- Python 3.9 or newer, standard library only.

From this folder:

```
python run.py --task rust-review --arms high,high+gearsecond --runs 10 --out results/rust-review
python summarize.py results/rust-review
```

- **Arms:** each arm is `<effort>` or `<effort>+<variant>`, where effort is `low`,
  `medium`, `high`, `xhigh` or `max`. A variant arm appends that skill's body to Claude
  Code's default system prompt. That's how an always-on install delivers it, and it avoids
  the extra turn a skill costs to load.
- **Variants:** `gearsecond` is the shipped skill, `../plugins/gearsecond/skills/gearsecond/SKILL.md`. Any other skill file placed in
  `variants/<name>.md` can be compared as `+<name>`, for example
  `--arms high,high+gearsecond,high+mydraft`.
- **Style prompts:** when a problem brings its own system text (the style task's
  compact style), the skill is appended after it. Later instructions tend to win, so
  that's the hardest case for the requested style to survive.
- **Other options:**
  - `--cli` picks the agent CLI.
  - `--model` picks the model (defaults: `claude-opus-5-5`, `grok-4.7`). Summaries also
    name the model that actually answered when it differs, for example `grok-4.7` is
    served as `grok-4.7-build`.
  - `--ids` limits the problems.
  - `--budget-usd` stops starting new runs at a spending limit.
- **Limits:** a run that hits a rate or usage limit isn't saved. Rerun the same command
  once the limit resets.
- **Interruptions:** runs that already finished are skipped, so an interrupted run can be
  resumed with the same command.
- **Skill versions:** a results folder holds one version of each variant. If a variant's
  text has changed, the runner refuses to add to an old folder; use a new `--out`.

## Isolation

Each session is isolated from the machine that runs it, so anyone on the same CLI version
gets the same context: the CLI's own default system prompt and built-in skills, nothing
personal.

- **Claude Code:** no tools, no MCP servers, no settings sources (so no personal plugins,
  hooks, CLAUDE.md or memory), and a fresh empty working directory.
- **Grok CLI:** no tools, no web search, no subagents, no plan mode, at most 5 turns (Grok sometimes writes a one-line preamble turn before the answer), and
  a fresh empty working directory.
  - Grok also reads Claude Code's skills, plugins and CLAUDE.md from the home folder, so
    each run gets an empty `HOME`/`USERPROFILE`.
  - `GROK_HOME` still points at the real `~/.grok`, so the login keeps working.
  - The skill goes in through `--rules`, which appends to Grok's system prompt.

- **Local models (LM Studio, `--cli lmstudio`):** there's no agent. The runner calls the
  local OpenAI-compatible server (default `http://localhost:2345/v1`, override with
  `LMSTUDIO_URL`). The task is the user message, and the skill, if any, is the only system
  message.
  - **Model settings:** sampling, context and reasoning budget come from the model's own
    LM Studio settings, which the runner can't read. Pass them with `--reasoning-budget`
    and `--note` so the manifest records them.
  - **Hitting the budget:** a run whose reasoning reaches that budget is reported as
    hitting it, so the summary shows how often each arm finishes within budget.
  - **Run order:** one run at a time; a single GPU would only queue them.
  - **Reasoning style:** LM Studio returns the full reasoning text, so the summary also
    reports its style (articles per word, words per line).
  - **Effort:** arms use effort `default` to keep the model's own setting.
  - **`@user` arms:** `default+gearsecond@user` puts the skill at the top of the user
    message instead. Some reasoning models pay little attention to the system prompt.
- **Gemini API (`--cli gemini`):** Gemini and Gemma models through Google's
  OpenAI-compatible endpoint, set up the same way as LM Studio. The key comes from
  `GEMINI_API_KEY` or a `GEMINI_API_KEY=...` line in `benchmark/.env`, which git ignores.
  Free-tier limits are per minute: runs go one at a time, and a rate-limited request waits
  (30 s, then up to 8 min) and retries. A run that still fails isn't saved, so rerunning the
  same command fills the gaps.
  - **Thinking tokens:** this endpoint has no reasoning-token field, so thinking is
    `total_tokens − prompt_tokens − completion_tokens`. Google's native API reports the same
    quantity as `thoughtsTokenCount`, and its totals add up the same way.
- **`quick` task:** for slow local models, a short Python review with 4 planted bugs,
  4 moderate maths problems and 2 style prompts.

The default prompt changes between CLI versions, so every results folder records the CLI
and version used (`manifest.json`). Other things to compare when reproducing:

- `skills`: each variant's sha256, with its exact text saved as `skill-<variant>.md`.
- the per-problem prompt hashes.
- the runner and scorer hashes.

## Results folder

```
results/<name>/
  manifest.json      CLI and version, model, exact CLI arguments, hashes, timestamps
  skill-<variant>.md the exact skill text each variant arm used
  summary.md / .json written by summarize.py
  runs/<problem>/<arm>/run-NN/
    raw.json         the CLI's full JSON output for that run (Grok's local path field removed)
    reply.md         the reply text
```

`summarize.py` rescores every reply from `raw.json`, so its tables can always be rebuilt
from the committed raw files.

## Statistics

Thinking length varies a lot between identical runs, sometimes threefold on hard maths, so
single runs prove nothing.

- **Interval and test:** `summarize.py` reports the change in mean thinking tokens against
  the baseline arm, with a 95% bootstrap confidence interval and a two-sided permutation
  test. Both use 10,000 resamples and a fixed seed, so reruns of the summary give
  identical numbers.
- **Several problems:** per-problem means are summed, and resampling stays within each
  problem.
- **Run counts:** use at least 5 runs per arm, and 10 for publishable numbers. With 2 runs
  per arm, the smallest possible p-value is 0.33.
- **Run order:** runs are shuffled with a fixed seed and interleaved across arms, so drift
  over time (load, model updates) affects every arm equally.
