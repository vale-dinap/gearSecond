---
name: gearsecond
description: >
  Fast, dense thinking: reason in short bursts of key inferences, no filler,
  so answers arrive sooner and use fewer thinking tokens. Changes only the
  thinking; the reply keeps whatever style it would otherwise have. Use for /gearsecond or "gear second". Stays on until "stop gearsecond".
---

# GearSecond

Think like a sprinter; answer the way you were asked to.

Thinking is scratch work only you read. Every thinking token costs time and
money and buys nothing unless it moves you toward the answer, so use the fewest
that still get it right. Stays on for the rest of the session, until "stop
gearsecond". Never mention it in replies, and don't spend thinking on following
it.

## Thinking

These rules are not optional: thinking that breaks them is wasted.

1. **Telegram, not prose.** One fact or inference per line, about 4 to 10
   words. Never a full sentence; if you catch one, cut it to its facts.
2. **Drop the glue:** articles (a, an, the), glue verbs (is, are, was, be, do,
   will, would), I/we/you, filler (also, just, really, basically, properly) and
   self-talk (hmm, okay, well, let me, I think). Never "clearly" or
   "obviously": check instead. Use the name, not "it" or "this", when the
   referent isn't obvious.
3. **Always keep meaning words:** negation (not, no, never, none), quantifiers
   (all, every, some, any, only, exactly, at least, at most), modality (must,
   should, can, may, might), logic (if, only if, unless, because, so, but, or,
   and), state (still, already, before, after) and uncertainty (likely, maybe).
   One word per idea: `so`, not therefore; `but`, not however.
4. **Symbols:** ASCII `=` `<` `>` `->` are fine. Avoid ∴ ≠ ✓ →: they often
   cost more tokens than a word.
5. **Doubt and correction in one line:** `? <question>: <answer>` instead of
   "wait…", and `wrong: <old>, <new>` instead of "actually…". Keep checking,
   briefly.
6. **Budget by step.** Routine step: one line or none. Plan for tool calls: one
   line (`read config -> run tests -> fix`). Hard step or real fork: up to
   three lines, more only for maths or logic steps that could actually be
   wrong. Aim for about 15 lines on a routine task. Never repeat an earlier
   line.
7. **Open on the first inference.** No restating the task, no "the user wants".
8. **Commit fast.** Pick an approach and go. Compare options only for a genuine
   close call, one line each.
9. **Trust what's settled.** Tool results, test output and established facts
   are done; don't re-derive them. Between tool calls: one to three lines on
   what the result means and the next move.
10. **Stop when done.** Answer clear and checked: stop and write the reply. No
    summary, no restating the answer, no drafting the reply in thinking.

Not: "Okay, so the tests pass for the normal case. But wait, I should check
`paginate`, because it computes the page count as `total / per_page`, which
rounds down, so when total isn't a multiple of per_page the last partial page
gets dropped. Actually, what happens when total is 0?"

But:

```
tests ok
paginate: pages = total / per_page rounds down, so last partial page lost
fix: pages = (total + per_page - 1) / per_page
? total = 0: 0 pages, ok
```

## Never trade away correctness

Cut words, not checks.

- Keep exact: numbers, signs, units, code, names, paths, errors.
- Hard logic or maths: write each step that could be wrong, in short form.
  Skip only the obvious ones.
- One targeted check on a non-trivial result (substitute back, run the test,
  try the edge case), then stop.

## Reply

If the user, the project or another skill has set a reply style (concise,
terse, caveman-style, formal, a fixed format), follow it exactly. It overrides
anything in this skill. This mode changes only how you think.

With no such request, write the reply as you normally would: don't make it
longer to make up for the short thinking, don't explain reasoning in it that you
wouldn't otherwise have explained, and keep the thinking shorthand out of it and
out of files, commits, docs and messages.

Recap for thinking: no full sentences; drop articles, glue verbs, pronouns,
filler and self-talk; keep not, all, only, can, must, if, because, but, still;
at most 3 lines per step; one check, then stop.
