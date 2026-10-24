"""Backends the benchmark can drive: agent CLIs (Claude Code, Grok CLI) and a local
OpenAI-compatible server (LM Studio). Each one runs a single isolated request and reads its
output into the same fields, so run.py and summarize.py stay backend-agnostic.

invoke(model, effort, prompt, system, timeout, tmp) returns the raw response as a dict.
extract(raw) returns:
  text            the reply
  thinking        reasoning tokens the provider counted (not an estimate from visible text)
  reasoning_text  the full reasoning, when the backend exposes it (LM Studio); else ""
  output          all output tokens, reasoning included
  cost            USD at list prices, as the backend reports it (0 for local models)
  seconds         run duration
  failed          the run produced no usable reply
  retry           a transient failure (rate or usage limit, auth, server down): don't save it
  served          model id(s) that actually answered
"""
import json
import os
import re
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path


def _version(cmd):
    out = subprocess.run([cmd, "--version"], capture_output=True, text=True, encoding="utf-8").stdout
    return out.split()[1] if out.startswith("grok") else out.split()[0]


class _AgentCLI:
    """Shared runner for agent CLIs: empty cwd and HOME, prompt and system text as files."""
    parallel_default = 6

    def invoke(self, model, effort, prompt, system, timeout, tmp):
        cwd, home = tmp / "cwd", tmp / "home"  # both stay empty; inputs sit beside them
        cwd.mkdir()
        home.mkdir()
        prompt_file = tmp / "prompt.txt"
        prompt_file.write_text(prompt, encoding="utf-8")
        append_file = None
        if system:
            append_file = tmp / "append.md"
            append_file.write_text(system, encoding="utf-8")
        try:
            r = subprocess.run(self.command(model, effort, prompt_file, append_file),
                               input=self.stdin(prompt), cwd=cwd, env=self.env(home),
                               capture_output=True, text=True, encoding="utf-8", timeout=timeout)
            return json.loads(r.stdout)
        except subprocess.TimeoutExpired:
            return {"runner_error": f"timeout after {timeout} s", "is_error": True}
        except Exception as e:  # unparseable output: keep a record (no paths), count as failed
            return {"runner_error": type(e).__name__, "is_error": True}


class Claude(_AgentCLI):
    name = "claude"
    default_model = "claude-opus-5-5"
    isolation = "no tools, no MCP, no settings sources, fresh empty cwd per run"

    def version(self):
        return _version("claude")

    def command(self, model, effort, prompt_file, append_file):
        args = ["claude", "-p", "--output-format", "json", "--model", model,
                *(["--effort", effort] if effort != "default" else []),
                "--tools", "", "--strict-mcp-config", "--setting-sources", "", "--no-session-persistence"]
        if append_file:
            args += ["--append-system-prompt-file", str(append_file)]
        return args

    def stdin(self, prompt):
        return prompt  # stdin avoids Windows' ~32k command-line limit

    def env(self, home):
        return None

    def scrub(self, raw):
        return raw

    def extract(self, raw):
        usage = raw.get("usage") or {}
        text = raw.get("result") or ""
        return {"text": text,
                "thinking": (usage.get("output_tokens_details") or {}).get("thinking_tokens") or 0,
                "reasoning_text": "",
                "output": usage.get("output_tokens") or 0,
                "cost": raw.get("total_cost_usd") or 0,
                "seconds": (raw.get("duration_ms") or 0) / 1000 or (raw.get("runner") or {}).get("wall_s", 0),
                "failed": bool(raw.get("is_error")) or not text,
                "retry": raw.get("api_error_status") == 429,
                "served": sorted(raw.get("modelUsage") or {})}


class Grok(_AgentCLI):
    name = "grok"
    default_model = "grok-4.7"
    isolation = ("no tools, no web search, no subagents, no plan mode, at most 5 turns (Grok sometimes writes a preamble turn first), empty HOME so "
                 "~/.claude skills/plugins/CLAUDE.md aren't picked up (GROK_HOME keeps the login), "
                 "fresh empty cwd per run")

    def version(self):
        return _version("grok")

    def command(self, model, effort, prompt_file, append_file):
        args = ["grok", "--prompt-file", str(prompt_file), "--output-format", "json", "-m", model,
                *(["--reasoning-effort", effort] if effort != "default" else []),
                "--tools", "", "--disable-web-search", "--no-subagents", "--no-plan", "--max-turns", "5"]
        if append_file:
            args += ["--rules", Path(append_file).read_text(encoding="utf-8")]
        return args

    def stdin(self, prompt):
        return None  # the prompt goes in through --prompt-file

    def env(self, home):
        env = dict(os.environ)
        env["GROK_HOME"] = env.get("GROK_HOME") or str(Path.home() / ".grok")
        env["HOME"] = env["USERPROFILE"] = str(home)
        return env

    def scrub(self, raw):
        raw.pop("cwd", None)  # contains the local user path
        return raw

    def extract(self, raw):
        usage = raw.get("usage") or {}
        text = raw.get("text") or ""
        error = raw.get("type") == "error"
        return {"text": text,
                "thinking": usage.get("reasoning_tokens") or 0,
                "reasoning_text": "",  # Grok's `thought` is a summary, not the reasoning itself
                "output": usage.get("output_tokens") or 0,
                "cost": raw.get("total_cost_usd") or 0,
                "seconds": (raw.get("runner") or {}).get("wall_s", 0),
                # A run cut off by --max-turns ends on a preamble, not an answer.
                "failed": (error or bool(raw.get("is_error")) or not text
                           or raw.get("stopReason") == "max_turn_requests"),
                "retry": error and "runner_error" not in raw,
                "served": sorted(raw.get("modelUsage") or {})}


class LMStudio:
    """Local models through LM Studio's OpenAI-compatible server. There's no agent here: the
    request carries only the skill (if any) as system message and the task as user message.
    Sampling, context and reasoning budget come from the model's LM Studio settings, which the
    runner can't read, so pass them with --note and --reasoning-budget."""
    name = "lmstudio"
    default_model = "openai/gpt-oss-20b"
    parallel_default = 1  # one GPU: requests would only queue
    # Another client loading or swapping models makes the server reject requests (HTTP 400)
    # for a while: wait and retry, and never score a rejected request as a wrong answer.
    backoff_s = (30, 60, 120)
    transient_http = (400, 429, 500, 503)
    url = os.environ.get("LMSTUDIO_URL", "http://localhost:2345/v1")
    isolation = ("raw chat-completions API, no agent system prompt: the skill (if any) is the only "
                 "system message; model settings (sampling, context, reasoning budget) from LM Studio")

    def version(self):
        try:  # `lms version` prints a banner and the CLI commit, not a release number
            out = subprocess.run(["lms", "version"], capture_output=True, text=True, timeout=20).stdout
            commit = re.search(r"CLI commit:\s*(\w+)", out)
            return f"lms-commit-{commit.group(1)}" if commit else "unknown"
        except Exception:
            return "unknown"

    def command(self, model, effort, prompt_file, append_file):
        return ["POST", f"{self.url}/chat/completions", f"model={model}",
                *([f"reasoning_effort={effort}"] if effort != "default" else [])]

    def headers(self):
        return {"Content-Type": "application/json"}

    def effort_fields(self, effort):
        return {"reasoning_effort": effort}

    def _post(self, body, timeout):
        req = urllib.request.Request(f"{self.url}/chat/completions", data=json.dumps(body).encode(),
                                     headers=self.headers())
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())

    def warmup(self, model):
        """Load the model before timing anything; the reply is discarded."""
        self._post({"model": model, "messages": [{"role": "user", "content": "Reply with OK."}]}, 1800)

    def invoke(self, model, effort, prompt, system, timeout, tmp):
        for wait in (*self.backoff_s, None):
            t0 = time.time()
            raw = self._attempt(model, effort, prompt, system, timeout)
            if not raw.get("transient") or wait is None:
                raw["attempt_s"] = round(time.time() - t0, 1)  # the run's own time, without retry waits
                return raw
            time.sleep(wait)

    def _attempt(self, model, effort, prompt, system, timeout):
        messages = ([{"role": "system", "content": system}] if system else []) + \
                   [{"role": "user", "content": prompt}]
        body = {"model": model, "messages": messages, "stream": False}
        if effort != "default":
            body.update(self.effort_fields(effort))
        try:
            return self._post(body, timeout)
        except TimeoutError:
            return {"runner_error": f"timeout after {timeout} s", "is_error": True}
        except urllib.error.HTTPError as e:
            return {"runner_error": f"HTTP {e.code}", "is_error": True, "transient": e.code in self.transient_http}
        except (urllib.error.URLError, ConnectionError):
            return {"runner_error": "server unreachable", "is_error": True, "transient": True}

    def scrub(self, raw):
        return raw

    def extract(self, raw):
        choice = (raw.get("choices") or [{}])[0]
        msg = choice.get("message") or {}
        usage = raw.get("usage") or {}
        text = msg.get("content") or ""
        return {"text": text,
                "thinking": (usage.get("completion_tokens_details") or {}).get("reasoning_tokens") or 0,
                # gpt-oss puts it in `reasoning`; <think>-tag models in `reasoning_content`
                "reasoning_text": msg.get("reasoning_content") or msg.get("reasoning") or "",
                "output": usage.get("completion_tokens") or 0,
                "cost": 0,
                # older runs have no attempt_s: their wall time includes any retry waits
                "seconds": raw.get("attempt_s") or (raw.get("runner") or {}).get("wall_s", 0),
                "failed": (bool(raw.get("is_error")) or not text
                           or choice.get("finish_reason") == "length"),
                # a request the server never answered says nothing about the model: don't
                # save or score it (a timeout is the model's own failure, so it still counts)
                "retry": bool(raw.get("transient")) or (
                    "runner_error" in raw and not raw["runner_error"].startswith("timeout")),
                "served": [raw["model"]] if raw.get("model") else []}


class Gemini(LMStudio):
    """Google's Gemini API (Gemini and Gemma models) through its OpenAI-compatible endpoint.
    The key comes from GEMINI_API_KEY, or a `GEMINI_API_KEY=...` line in benchmark/.env
    (git-ignored). Free-tier rate limits are low and per minute, so runs go one at
    a time and a rate-limited request waits and retries; one still failing after that isn't
    saved, so rerunning the same command fills the gaps."""
    name = "gemini"
    default_model = "gemma-4-31b-it"
    parallel_default = 1
    backoff_s = (30, 60, 120, 240, 480)  # free-tier limits are per minute; wait them out
    transient_http = (429, 500, 503)  # a 400 here is a bad request, not a busy server
    url = "https://generativelanguage.googleapis.com/v1beta/openai"
    isolation = ("raw chat-completions API (Gemini API, OpenAI-compatible endpoint), no agent "
                 "system prompt: the skill (if any) is the only system message")

    def version(self):
        return "gemini-api-v1beta-openai"

    def warmup(self, model):
        pass  # a hosted model has nothing to load

    def effort_fields(self, effort):
        # Gemma's thinking is on/off: thinking_level "high" = on, "minimal" = off. In a raw
        # request the documented passthrough is a literal "extra_body" key.
        return {"extra_body": {"google": {"thinking_config": {"thinking_level": effort}}}}

    def command(self, model, effort, prompt_file, append_file):
        return ["POST", f"{self.url}/chat/completions", f"model={model}",
                *([f"thinking_level={effort}"] if effort != "default" else [])]

    def key(self):
        if os.environ.get("GEMINI_API_KEY"):
            return os.environ["GEMINI_API_KEY"]
        env = Path(__file__).parent / ".env"
        if env.exists():
            for line in env.read_text(encoding="utf-8").splitlines():
                name, _, value = line.partition("=")
                if name.strip() == "GEMINI_API_KEY":
                    return value.strip().strip('"')
        raise SystemExit("set GEMINI_API_KEY or add it to benchmark/.env")

    def headers(self):
        return {**super().headers(), "Authorization": f"Bearer {self.key()}"}

    def extract(self, raw):
        # This endpoint has no reasoning-token field, but total_tokens includes the thinking:
        # the native API's usageMetadata shows total = prompt + candidates + thoughts.
        x = super().extract(raw)
        # Gemma's reasoning arrives inside the content as <thought>...</thought>, not in a
        # separate field: score only the answer and keep the reasoning for the style table.
        thoughts = re.findall(r"<thought>(.*?)</thought>", x["text"], flags=re.S)
        if thoughts:
            x["reasoning_text"] = "\n".join(thoughts)
            x["text"] = re.sub(r"<thought>.*?</thought>", "", x["text"], flags=re.S).strip()
            x["failed"] = x["failed"] or not x["text"]
        u = raw.get("usage") or {}
        x["thinking"] = max(u.get("total_tokens", 0) - u.get("prompt_tokens", 0) - u.get("completion_tokens", 0), 0)
        x["output"] = (u.get("completion_tokens") or 0) + x["thinking"]
        return x

    def models(self):
        req = urllib.request.Request(f"{self.url}/models", headers=self.headers())
        with urllib.request.urlopen(req, timeout=60) as resp:
            return [m["id"] for m in json.loads(resp.read())["data"]]


CLIS = {c.name: c for c in (Claude(), Grok(), LMStudio(), Gemini())}
