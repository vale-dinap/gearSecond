"""Task definitions and scoring shared by run.py and summarize.py.

A task yields problems; each problem has an id, the prompt sent to the model, an optional
system-prompt addition and a scorer that turns the reply into {"score": 0..1, ...details}. Scoring lives here, not in run.py,
so summarize.py can rescore saved replies after a scorer fix without paying for new runs.
"""
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent
TASKS = ROOT / "tasks"

# Arms: an effort level, optionally with a skill variant appended to the system prompt.
# `gearsecond` is the skill this repo ships; other variants live in variants/<name>.md.
# `default` leaves the backend's own effort setting alone (e.g. a local model's preset).
# `<effort>+<variant>@user` puts the skill at the top of the user message, not the system
# prompt, for models that pay little attention to system prompts.
EFFORTS = ("default", "low", "medium", "high", "xhigh", "max")
VARIANTS = {"gearsecond": ROOT.parent / "plugins" / "gearsecond" / "skills" / "gearsecond" / "SKILL.md",
            **{p.stem: p for p in sorted((ROOT / "variants").glob("*.md"))}}


def parse_arm(arm):
    """'high' -> ('high', None); 'high+draft' -> ('high', 'draft'); 'high+draft@user' -> ('high', 'draft')."""
    effort, _, variant = arm.partition("+")
    variant = variant.removesuffix("@user")
    if effort not in EFFORTS or (variant and variant not in VARIANTS):
        raise ValueError(f"bad arm {arm!r}: use <effort>, <effort>+<variant> or "
                         f"<effort>+<variant>@user; effort in {EFFORTS}, variant in {sorted(VARIANTS)}")
    return effort, variant or None


def skill_in_user_message(arm):
    return arm.endswith("@user")


# --- rust-review: planted bugs marked with `// @BUG:<name>`, stripped before sending ---

REVIEW_SLACK_BEFORE, REVIEW_SLACK_AFTER = 3, 2
REVIEW_PROMPT = (
    "Please review this {what} before it is merged. Look for real defects: {kinds}. "
    "Skip style nits.\n\n"
    "```{lang}\n{code}\n```\n\n"
    "Explain the problems you find. Then end your reply with a section that starts with the "
    "line `ISSUES:` and lists one defect per line as `L<line>: <short description>`."
)
RUST_REVIEW = {"what": "Rust module (src/lib.rs of a small inventory service)", "lang": "rust",
               "kinds": "logic errors, panics, integer overflow, undefined behaviour, memory "
                        "safety and concurrency problems", "comment": "//"}


def load_review(task_dir, file="src/lib.rs", spec=RUST_REVIEW, pid="lib.rs"):
    bugs = defaultdict(list)
    lines = []
    marker = re.compile(r"\s*" + re.escape(spec["comment"]) + r" @BUG:(\w+)$")
    for n, raw in enumerate((task_dir / file).read_text(encoding="utf-8").splitlines(), 1):
        m = marker.search(raw)
        if m:
            bugs[m.group(1)].append(n)
            raw = raw[: m.start()]
        lines.append(f"{n:>4} | {raw}")
    prompt = REVIEW_PROMPT.format(code="\n".join(lines), **spec)

    def score(reply):
        # The last ISSUES heading; some models drop the colon or wrap it in markdown.
        heads = list(re.finditer(r"ISSUES\b\**:?", reply))
        tail = reply[heads[-1].end():] if heads else ""
        # Bullets, bold and backticks may precede the line number: "- **L46:**", "`L46`".
        cited = [int(x) for x in re.findall(r"^[\s\-*`]*L(\d+)", tail, flags=re.M)]

        def hits(c, marks):
            return any(m - REVIEW_SLACK_BEFORE <= c <= m + REVIEW_SLACK_AFTER for m in marks)

        found = sorted(b for b, marks in bugs.items() if any(hits(c, marks) for c in cited))
        extra = [c for c in cited if not any(hits(c, marks) for marks in bugs.values())]
        return {"score": len(found) / len(bugs), "found": len(found), "of": len(bugs),
                "missed": sorted(set(bugs) - set(found)), "extra_lines": extra}

    return [{"id": pid, "prompt": prompt, "score": score}]


# --- counting: exact-answer problems, answers brute-forced by verify_answers.py ---

ANSWER_SUFFIX = ("\n\nWork it out by reasoning; do not write or run code. "
                 "End your reply with a final line of the form: ANSWER: <answer>")


def _norm(s):
    return re.sub(r"[\s,`*$]", "", s).rstrip(".").upper()


def load_counting(task_dir):
    out = []
    for p in json.loads((task_dir / "problems.json").read_text(encoding="utf-8")):
        def score(reply, expected=p["answer"]):
            m = re.findall(r"ANSWER:\s*(.+)", reply)
            got = m[-1].strip() if m else ""
            return {"score": float(_norm(got) == _norm(expected)), "got": got, "expected": expected}
        out.append({"id": p["id"], "prompt": p["question"] + ANSWER_SUFFIX, "score": score})
    return out


# --- style: does the reply keep a style requested by the user or the system prompt? ---

ARTICLES = re.compile(r"\b(a|an|the)\b", re.I)
SHORTHAND = re.compile("[∴→✓✗≠]")


def _prose(reply):
    """Reply text without code blocks or inline code, for sentence and word counts."""
    return re.sub(r"`[^`]*`", " ", re.sub(r"```.*?```", " ", reply, flags=re.S))


def _article_rate(text):
    words = re.findall(r"[A-Za-z']+", text)
    return len(ARTICLES.findall(text)) / max(len(words), 1)


def style_check(kind, limit, reply):
    text = _prose(reply)
    rate = _article_rate(text)
    if kind == "max_sentences":
        n = len(re.findall(r"[.!?](?=\s|$)", text.strip()))
        return {"score": float(0 < n <= limit), "sentences": n, "article_rate": rate}
    if kind == "numbered_items":
        n = len(re.findall(r"^\s*\d+[.)]\s", reply, flags=re.M))
        return {"score": float(n == limit), "items": n, "article_rate": rate}
    if kind == "max_articles":
        return {"score": float(rate < limit), "article_rate": rate}
    if kind == "normal_prose":
        # Symbols alone don't fail a reply ("A → B → C" is fine prose); they're reported so a
        # reader can spot leaked shorthand, which would also show up as a low article rate.
        return {"score": float(rate > limit), "article_rate": rate,
                "shorthand_symbols": len(SHORTHAND.findall(reply))}
    raise ValueError(kind)


def load_style(task_dir):
    out = []
    for p in json.loads((task_dir / "problems.json").read_text(encoding="utf-8")):
        out.append({"id": p["id"], "prompt": p["prompt"], "system": p.get("system", ""),
                    "score": lambda reply, k=p["check"], lim=p["limit"]: style_check(k, lim, reply)})
    return out


# --- quick: a short mix for slow local models (one review, four maths, two styles) ---

PY_REVIEW = {"what": "Python module (orders.py of a small shop backend)", "lang": "python",
             "kinds": "logic errors, crashes and behaviour that contradicts the docstrings",
             "comment": "#"}


def load_quick(task_dir):
    styles = {p["id"]: p for p in load_style(TASKS / "style")}
    return (load_review(task_dir, "orders.py", PY_REVIEW, "orders.py")
            + load_counting(task_dir)
            + [styles["default"], styles["two-sentences"]])


LOADERS = {"rust-review": load_review, "counting": load_counting, "style": load_style,
           "quick": load_quick}


def load_task(name, ids=None):
    if name not in LOADERS:
        raise ValueError(f"unknown task {name!r}; choose from {sorted(LOADERS)}")
    problems = LOADERS[name](TASKS / name)
    if ids:
        problems = [p for p in problems if p["id"] in ids]
    return problems
