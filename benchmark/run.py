"""Run a benchmark task through a backend and save everything needed to reproduce it.

Backends (see clis.py): Claude Code and Grok CLI, isolated from the machine they run on
(no tools, no personal plugins, hooks, memory or instruction files, fresh empty working
directory), and LM Studio's local OpenAI-compatible server. A `+<variant>` arm appends that
skill's body (frontmatter stripped) to the system prompt, which is how an always-on install
would deliver it; `+<variant>@user` puts it at the top of the user message instead.

Output layout (resumable: finished runs are skipped when rerun with the same --out):
  <out>/manifest.json            backend and version, model, flags, hashes, timestamps
  <out>/skill-<variant>.md       exact skill text each variant arm used
  <out>/runs/<problem>/<arm>/run-NN/{raw.json, reply.md}

Usage:
  python run.py --task rust-review --arms high,high+gearsecond --runs 10 --out results/x
  python run.py --cli grok --task rust-review --arms high,high+gearsecond --runs 10 --out results/y
  python run.py --cli lmstudio --model openai/gpt-oss-20b --task quick \\
      --arms default,default+gearsecond,default+gearsecond@user --runs 5 \\
      --reasoning-budget 4096 --note "context 32k, LM Studio default sampling" --out results/z
"""
import argparse
import hashlib
import json
import platform
import random
import re
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import bench
from clis import CLIS


def sha256(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def skill_body(path):
    text = path.read_text(encoding="utf-8")
    parts = re.split(r"^---\s*$", text, maxsplit=2, flags=re.M)
    if len(parts) != 3:
        sys.exit(f"{path}: frontmatter not delimited by --- lines")
    return parts[2].strip()


def messages_for(arm, problem, bodies):
    """(system text, user prompt) for one run. The problem's own system text (e.g. a requested
    reply style) comes first and the skill after it, the position most likely to override
    earlier instructions, so style tasks test the worst case. An @user arm moves the skill to
    the top of the user message instead."""
    skill = bodies.get(bench.parse_arm(arm)[1], "")
    if bench.skill_in_user_message(arm):
        return problem.get("system", ""), f"{skill}\n\n---\n\n{problem['prompt']}"
    return "\n\n".join(t for t in (problem.get("system", ""), skill) if t), problem["prompt"]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--task", required=True, choices=sorted(bench.LOADERS))
    ap.add_argument("--arms", required=True, help="comma list, e.g. high,high+gearsecond")
    ap.add_argument("--runs", type=int, required=True, help="runs per problem per arm")
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--cli", default="claude", choices=sorted(CLIS))
    ap.add_argument("--ids", help="comma list of problem ids (default: all)")
    ap.add_argument("--model", help="default: the backend's benchmark default (see clis.py)")
    ap.add_argument("--parallel", type=int, help="default: 6 for agent CLIs, 1 for local models")
    ap.add_argument("--budget-usd", type=float, help="stop starting new runs once spend reaches this")
    ap.add_argument("--timeout", type=int, default=1800, help="seconds per run")
    ap.add_argument("--reasoning-budget", type=int,
                    help="the model's reasoning-token cap, if one is set outside the runner (recorded; "
                         "runs that reach it are reported as hitting the budget)")
    ap.add_argument("--note", help="free text recorded in the manifest, e.g. local model settings")
    a = ap.parse_args()

    cli = CLIS[a.cli]
    model = a.model or cli.default_model
    arms = a.arms.split(",")
    for arm in arms:
        bench.parse_arm(arm)
    problems = bench.load_task(a.task, a.ids.split(",") if a.ids else None)
    if not problems:
        sys.exit("no problems selected")
    out = a.out.resolve()
    out.mkdir(parents=True, exist_ok=True)

    bodies = {}
    for arm in arms:
        variant = bench.parse_arm(arm)[1]
        if variant and variant not in bodies:
            bodies[variant] = skill_body(bench.VARIANTS[variant])
            saved = out / f"skill-{variant}.md"
            if saved.exists() and saved.read_text(encoding="utf-8") != bodies[variant]:
                sys.exit(f"{saved} differs from the current {variant} skill; use a new --out")
            saved.write_text(bodies[variant], encoding="utf-8")

    version = cli.version()
    manifest_path = out / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    if manifest and manifest.get("cli", "claude") != cli.name:
        sys.exit(f"{out} holds {manifest.get('cli', 'claude')} results; use a new --out for {cli.name}")
    if manifest and manifest.get("model", model) != model:
        sys.exit(f"{out} holds {manifest['model']} results; use a new --out for {model}")
    if manifest and manifest.get("cli_version", manifest.get("claude_code_version")) != version:
        print(f"warning: results so far used {cli.name} "
              f"{manifest.get('cli_version', manifest.get('claude_code_version'))}, now {version}")

    def describe(arm):
        effort, variant = bench.parse_arm(arm)
        where = ("skill-{v}.md at the top of the user message" if bench.skill_in_user_message(arm)
                 else "problem system text, then skill-{v}.md, appended to the system prompt")
        return cli.command(model, effort, "<prompt.txt>", None) + (
            [f"<{where.format(v=variant)}>"] if variant else [])

    manifest.update({
        "task": a.task, "cli": cli.name, "cli_version": version, "model": model,
        "arms": arms, "runs_per_arm": a.runs,
        "problems": {p["id"]: sha256(p.get("system", "") + "\n\n" + p["prompt"]) for p in problems},
        "skills": {v: {"sha256": sha256(b), "file": f"skill-{v}.md",
                       "source": str(bench.VARIANTS[v].relative_to(bench.ROOT.parent)).replace("\\", "/")}
                   for v, b in bodies.items()},
        "cli_args": {arm: describe(arm) for arm in arms},
        "isolation": cli.isolation,
        "platform": platform.platform(), "python": platform.python_version(),
        "runner_sha256": sha256(Path(__file__).read_text(encoding="utf-8")),
        "bench_sha256": sha256(Path(bench.__file__).read_text(encoding="utf-8")),
    })
    if a.reasoning_budget:
        manifest["reasoning_budget"] = a.reasoning_budget
    if a.note:
        manifest["note"] = a.note
    manifest.pop("claude_code_version", None)
    manifest.setdefault("started_utc", datetime.now(timezone.utc).isoformat(timespec="seconds"))
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    if hasattr(cli, "warmup"):
        print(f"loading {model}…", flush=True)
        cli.warmup(model)

    # Interleave arms and shuffle with a fixed seed so time-of-day drift hits every arm alike.
    jobs = [(p, arm, n) for n in range(1, a.runs + 1) for p in problems for arm in arms]
    random.Random(0).shuffle(jobs)
    spent = [0.0]
    lock = threading.Lock()

    def run(job):
        p, arm, n = job
        d = out / "runs" / p["id"] / arm.replace("+", "_").replace("@", "_at_") / f"run-{n:02d}"
        if (d / "raw.json").exists():
            return None
        with lock:
            if a.budget_usd is not None and spent[0] >= a.budget_usd:
                return f"skip {d.relative_to(out)}: budget reached"
        system, prompt = messages_for(arm, p, bodies)
        t0 = time.time()
        with tempfile.TemporaryDirectory(prefix="gearsecond-bench-") as tmp:
            raw = cli.invoke(model, bench.parse_arm(arm)[0], prompt, system, a.timeout, Path(tmp))
        raw = cli.scrub(raw)
        raw["runner"] = {"cli": cli.name, "arm": arm, "problem": p["id"], "run": n,
                         "wall_s": round(time.time() - t0, 1),
                         "finished_utc": datetime.now(timezone.utc).isoformat(timespec="seconds")}
        x = cli.extract(raw)
        if x["retry"]:  # rate/usage limit, auth or server problem: leave unsaved so a rerun retries it
            return f"retry later {d.relative_to(out)}: " \
                   f"{(raw.get('result') or raw.get('message') or raw.get('runner_error') or '')[:100]}"
        d.mkdir(parents=True, exist_ok=True)
        (d / "raw.json").write_text(json.dumps(raw, indent=2), encoding="utf-8")
        (d / "reply.md").write_text(x["text"], encoding="utf-8")
        with lock:
            spent[0] += x["cost"]
        s = p["score"](x["text"])["score"]
        return (f"{p['id']:<13} {arm:<26} run {n:>2}  score {s:.2f}  thinking {x['thinking']}  "
                f"{x['seconds']:.0f}s  spent ${spent[0]:.2f}")

    with ThreadPoolExecutor(a.parallel or cli.parallel_default) as ex:
        for fut in as_completed([ex.submit(run, j) for j in jobs]):
            if fut.result():
                print(fut.result(), flush=True)

    manifest["finished_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"done; spent ${spent[0]:.2f} this session. Summarize: python summarize.py {a.out}")


if __name__ == "__main__":
    main()
