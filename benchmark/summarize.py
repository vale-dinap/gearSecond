"""Summarize a results folder into Markdown tables (stdout, summary.md) and summary.json.

Replies are rescored from raw.json with the current scorers in bench.py, so a scorer fix
never needs new runs. Comparisons are against the baseline arm (default: the first arm in
the manifest): change in mean thinking tokens with a 95% bootstrap confidence interval and
a two-sided permutation-test p-value. With several problems, per-problem means are summed
and resampling stays within each problem (stratified).

Usage: python summarize.py results/<folder> [--baseline high]
"""
import argparse
import json
import random
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

import bench
from clis import CLIS

RESAMPLES = 10_000
CLI_NAMES = {"claude": "Claude Code", "grok": "Grok CLI", "lmstudio": "LM Studio", "gemini": "Gemini API"}


def load(folder):
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    problems = {p["id"]: p for p in bench.load_task(manifest["task"])}
    rows, skipped = [], 0
    cli = CLIS[manifest.get("cli", "claude")]
    for f in sorted((folder / "runs").glob("*/*/run-*/raw.json")):
        raw = json.loads(f.read_text(encoding="utf-8"))
        meta = raw["runner"]
        x = cli.extract(raw)
        if x["retry"]:  # saved before the runner skipped these: the server never answered
            skipped += 1
            continue
        rows.append({
            "problem": meta["problem"], "arm": meta["arm"], "run": meta["run"],
            "failed": x["failed"],
            **problems[meta["problem"]]["score"](x["text"]),
            "thinking": x["thinking"], "output": x["output"], "reply_chars": len(x["text"]),
            "seconds": x["seconds"], "cost": x["cost"], "served": x["served"],
            "reasoning_text": x["reasoning_text"],
        })
    return manifest, rows, skipped


def reasoning_style(text):
    """Telegram-style markers in visible reasoning: articles per word and words per line."""
    lines = [ln for ln in text.splitlines() if ln.strip()]
    words = sum(len(ln.split()) for ln in lines)
    return bench._article_rate(text), words / max(len(lines), 1)


def stratified_total(groups):
    """Sum over problems of the mean thinking per problem."""
    return sum(st.mean(v) for v in groups.values())


def compare(base, arm, rng):
    """base/arm: {problem: [thinking,...]} over the problems both arms ran."""
    keys = [k for k in base if k in arm]
    b = {k: base[k] for k in keys}
    t = {k: arm[k] for k in keys}
    if not stratified_total(b):
        return None  # baseline never thought: a relative change is undefined
    observed = stratified_total(t) / stratified_total(b) - 1
    boots = []
    for _ in range(RESAMPLES):
        den = stratified_total({k: rng.choices(b[k], k=len(b[k])) for k in keys})
        if den:  # a resample of all-zero baseline runs has no ratio; skip it
            boots.append(stratified_total({k: rng.choices(t[k], k=len(t[k])) for k in keys}) / den - 1)
    boots.sort()
    lo, hi = boots[int(0.025 * len(boots))], boots[int(0.975 * len(boots)) - 1]
    diff = stratified_total(t) - stratified_total(b)
    extreme = 0
    for _ in range(RESAMPLES):
        pb, pt = {}, {}
        for k in keys:
            pool = b[k] + t[k]
            rng.shuffle(pool)
            pb[k], pt[k] = pool[:len(b[k])], pool[len(b[k]):]
        extreme += abs(stratified_total(pt) - stratified_total(pb)) >= abs(diff) - 1e-9
    return observed, lo, hi, (extreme + 1) / (RESAMPLES + 1)


def served_note(manifest, rows):
    served = sorted({m for r in rows for m in r["served"]} - {manifest["model"]})
    return f" (served as {', '.join(f'`{m}`' for m in served)})" if served else ""


def skills_line(manifest):
    if "skills" in manifest:
        return ", ".join(f"{v} sha256 `{s['sha256'][:12]}`" for v, s in manifest["skills"].items())
    return f"gearsecond sha256 `{manifest['skill_sha256'][:12]}`"  # folders from before variants


def fmt_int(x):
    return f"{x:,.0f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", type=Path)
    ap.add_argument("--baseline")
    a = ap.parse_args()
    manifest, rows, skipped = load(a.folder)
    arms = [arm for arm in manifest["arms"] if any(r["arm"] == arm for r in rows)]
    baseline = a.baseline or arms[0]
    rng = random.Random(0)

    by = defaultdict(list)
    for r in rows:
        by[r["problem"], r["arm"]].append(r)
    problem_ids = sorted({r["problem"] for r in rows})

    out = [f"## {manifest['task']}", "",
           f"Model `{manifest['model']}`{served_note(manifest, rows)}, {CLI_NAMES[manifest.get('cli', 'claude')]} "
           f"{manifest.get('cli_version', manifest.get('claude_code_version', '?')).split()[0]}, "
           f"{skills_line(manifest)}, {manifest.get('started_utc', '?')[:10]}.", "",
           "| Problem | Arm | Runs | Quality | Thinking mean ± sd | Median | Range | Reply chars | Seconds | Cost/run |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    summary = {"manifest": manifest, "cells": [], "comparisons": []}
    for pid in problem_ids:
        for arm in arms:
            rs = by.get((pid, arm))
            if not rs:
                continue
            th = [r["thinking"] for r in rs]
            q = st.mean(r["score"] for r in rs)
            if "found" in rs[0]:
                qual = f"{st.mean(r['found'] for r in rs):.1f}/{rs[0]['of']} found"
            elif "article_rate" in rs[0]:
                qual = (f"{sum(r['score'] for r in rs):.0f}/{len(rs)} compliant, "
                        f"articles {st.mean(r['article_rate'] for r in rs):.1%}")
            else:
                qual = f"{sum(r['score'] for r in rs):.0f}/{len(rs)} correct"
            fails = sum(r["failed"] for r in rs)
            if manifest.get("reasoning_budget"):
                hits = sum(r["thinking"] >= 0.98 * manifest["reasoning_budget"] for r in rs)
                qual += f", {hits} hit budget"
            sd = st.stdev(th) if len(th) > 1 else 0
            out.append(f"| {pid} | {arm} | {len(rs)}{f' ({fails} failed)' if fails else ''} | {qual} | "
                       f"{fmt_int(st.mean(th))} ± {fmt_int(sd)} | {fmt_int(st.median(th))} | "
                       f"{fmt_int(min(th))}–{fmt_int(max(th))} | {fmt_int(st.mean(r['reply_chars'] for r in rs))} | "
                       f"{st.mean(r['seconds'] for r in rs):.0f} | ${st.mean(r['cost'] for r in rs):.3f} |")
            summary["cells"].append({"problem": pid, "arm": arm, "runs": len(rs), "failed": fails,
                                     "quality": q, "thinking": th,
                                     "cost_total": sum(r["cost"] for r in rs)})

    out += ["", f"Change in thinking tokens vs `{baseline}`"
            + (" (all problems, stratified)" if len(problem_ids) > 1 else "") + ":", "",
            "| Arm | Thinking change | 95% CI | p (permutation) | Quality change |", "|---|---|---|---|---|"]
    think = {arm: {pid: [r["thinking"] for r in by[pid, arm]] for pid in problem_ids if (pid, arm) in by}
             for arm in arms}
    quality = {arm: st.mean(r["score"] for r in rows if r["arm"] == arm) for arm in arms}
    for arm in arms:
        if arm == baseline:
            continue
        dq = quality[arm] - quality[baseline]
        result = compare(think[baseline], think[arm], rng)
        if result is None:
            out.append(f"| {arm} | n/a (no baseline thinking) | | | {dq:+.1%} |")
            continue
        obs, lo, hi, p = result
        out.append(f"| {arm} | {obs:+.1%} | {lo:+.1%} to {hi:+.1%} | {p:.4f} | {dq:+.1%} |")
        summary["comparisons"].append({"arm": arm, "baseline": baseline, "thinking_change": obs,
                                       "ci95": [lo, hi], "p": p, "quality_change": dq})
    if any(r["reasoning_text"] for r in rows):
        out += ["", "Reasoning style (visible reasoning, all problems): telegram style shows as fewer "
                "articles and shorter lines.", "",
                "| Arm | Articles per word | Words per line | Reasoning chars |", "|---|---|---|---|"]
        for arm in arms:
            texts = [r["reasoning_text"] for r in rows if r["arm"] == arm and r["reasoning_text"]]
            if texts:
                styles = [reasoning_style(t) for t in texts]
                out.append(f"| {arm} | {st.mean(s[0] for s in styles):.1%} | "
                           f"{st.mean(s[1] for s in styles):.1f} | {fmt_int(st.mean(len(t) for t in texts))} |")
                summary.setdefault("reasoning_style", {})[arm] = {
                    "article_rate": st.mean(s[0] for s in styles), "words_per_line": st.mean(s[1] for s in styles)}
    total = sum(r["cost"] for r in rows)
    cost_note = {"lmstudio": "no API cost (local model)", "gemini": "cost not reported by the API"}.get(
        manifest.get("cli"), f"total cost ${total:.2f} at list API prices")
    out += ["", f"{len(rows)} runs, {cost_note}."
            + (f" {skipped} runs left out: the server never answered them." if skipped else "")]
    if manifest.get("reasoning_budget"):
        out.append(f"Reasoning budget: {manifest['reasoning_budget']} tokens.")
    if manifest.get("note"):
        out.append(f"Note: {manifest['note']}")

    text = "\n".join(out)
    sys.stdout.reconfigure(encoding="utf-8")
    print(text)
    (a.folder / "summary.md").write_text(text + "\n", encoding="utf-8")
    (a.folder / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
