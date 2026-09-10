"""Run one bounded text task through an installed Claude Code or Grok CLI.

Announce model, channel and assignment to the user before invoking this command.
No tools are enabled. Authentication stays with the installed CLI. Each invocation
has a new output directory, a finite timeout, and no automatic retries.
"""
import argparse
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import subprocess
import time
import uuid


def command(adapter, executable, model, effort):
    common = [str(executable), "--model", model, "--output-format", "json"]
    if adapter == "claude-code":
        return common + ["--effort", effort, "--tools", "", "--setting-sources", "",
                         "--strict-mcp-config", "--max-turns", "1",
                         "--no-session-persistence", "-p"]
    if adapter == "grok":
        return common + ["--reasoning-effort", effort, "--tools", "", "--no-subagents",
                         "--disable-web-search", "--permission-mode", "plan",
                         "--max-turns", "1", "-p"]
    raise ValueError("Unsupported adapter")


def value(data, *keys):
    for key in keys:
        item = data.get(key)
        if type(item) in (int, float) and math.isfinite(item) and item >= 0:
            return item
    return None


def normalize(body, adapter, requested_model, effort, task_id, pool, elapsed):
    """Only report provider fields actually present; never infer cash charges."""
    reply = next((body[k] for k in ("result", "text", "response")
                  if isinstance(body.get(k), str)), None)
    failed = body.get("is_error") is True or str(body.get("status", "")).upper() in ("ERROR", "FAILED")
    if str(body.get("subtype", "")).startswith("error"):
        failed = True
    model_usage = body.get("modelUsage")
    if isinstance(model_usage, dict) and model_usage:
        sources = [(model, stats) for model, stats in model_usage.items() if isinstance(stats, dict)]
    else:
        model = body.get("model") if isinstance(body.get("model"), str) else "unresolved:" + requested_model
        usage = body.get("usage") if isinstance(body.get("usage"), dict) else {}
        sources = [(model, dict(usage, estimated_cost=body.get("total_cost_usd")))]
    entries = []
    for model, stats in sources:
        reasoning = value(stats, "reasoningTokens", "reasoning_tokens")
        # A single reported model permits attributing the call-level reasoning field.
        if reasoning is None and len(sources) == 1 and isinstance(body.get("usage"), dict):
            reasoning = value(body["usage"], "reasoning_tokens")
        measurements = {
            "input_tokens": ("token", value(stats, "inputTokens", "input_tokens")),
            "output_tokens": ("token", value(stats, "outputTokens", "output_tokens")),
            "reasoning_tokens": ("token", reasoning),
            "cache_read_input_tokens": ("token", value(stats, "cacheReadInputTokens", "cache_read_input_tokens")),
            "cache_creation_input_tokens": ("token", value(stats, "cacheCreationInputTokens", "cache_creation_input_tokens")),
            "estimated_api_cost": ("USD", value(stats, "costUSD", "estimated_cost")),
        }
        entries.append({"task_id": task_id, "event_id": str(uuid.uuid4()),
            "phase": "worker", "agent": f"{adapter}/{model}/requested-effort:{effort}",
            "pool": pool, "counter_mode": "delta", "scope": "own_call",
            "metrics": {key: {"unit": unit, "value": amount}
                        for key, (unit, amount) in measurements.items()}})
    return {"reply": reply, "provider_failed": failed,
            "models_reported": [model for model, _ in sources],
            "session_id": body.get("session_id", body.get("sessionId")),
            "elapsed_seconds": elapsed, "entries": entries}


def write_json(path, content):
    path.write_text(json.dumps(content, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def run(args):
    exe, workspace = args.executable.resolve(), args.workspace.resolve()
    if not exe.is_file() or not workspace.is_dir():
        raise ValueError("Provide an installed executable file and an existing workspace directory")
    if os.name == "nt" and exe.suffix.lower() != ".exe":
        raise ValueError("On Windows use the real .exe, not a .cmd/.bat wrapper")
    prompt = args.prompt_file.read_text(encoding="utf-8-sig")
    if not prompt.strip():
        raise ValueError("Prompt file is empty")
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=False)
    record = {"task_id": args.task_id, "adapter": args.adapter, "requested_model": args.model,
              "requested_effort": args.effort, "pool": args.pool, "status": "starting",
              "started_at": datetime.now(timezone.utc).isoformat(), "acceptance": "not_determined",
              "supported_operations": ["one_shot_text"], "timeout_seconds": args.timeout}
    write_json(out / "status.json", record)
    env = dict(os.environ)
    for name in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "XAI_API_KEY", "GROK_API_KEY"):
        env.pop(name, None)
    options = {"cwd": workspace, "env": env, "stdin": subprocess.PIPE,
               "stdout": subprocess.PIPE, "stderr": subprocess.PIPE}
    if os.name == "nt":
        options["creationflags"] = subprocess.CREATE_NO_WINDOW
    started = time.monotonic()
    # No shell expansion. For Grok the prompt is an argument; Claude reads stdin.
    argv = command(args.adapter, exe, args.model, args.effort)
    stdin = prompt.encode("utf-8")
    if args.adapter == "grok":
        argv.append(prompt)
        stdin = None
    try:
        process = subprocess.Popen(argv, **options)
    except OSError as exc:
        record.update(status="launch_failed", error_type=type(exc).__name__)
        write_json(out / "status.json", record)
        return record
    record.update(status="running", pid=process.pid)
    write_json(out / "status.json", record)
    timed_out = False
    try:
        stdout, stderr = process.communicate(stdin, timeout=args.timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        if os.name == "nt":
            try:
                subprocess.run(["taskkill.exe", "/PID", str(process.pid), "/T", "/F"],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                               creationflags=subprocess.CREATE_NO_WINDOW, timeout=10)
            except (OSError, subprocess.TimeoutExpired):
                record.update(status="timeout_cleanup_uncertain", automatic_retry=False)
                write_json(out / "status.json", record)
                return record
        else:
            process.kill()
        try:
            stdout, stderr = process.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            record.update(status="timeout_cleanup_uncertain", automatic_retry=False)
            write_json(out / "status.json", record)
            return record
    (out / "stdout.json").write_bytes(stdout)
    (out / "stderr.log").write_bytes(stderr)
    record.update(exit_code=process.returncode, elapsed_seconds=round(time.monotonic() - started, 3))
    try:
        body = json.loads(stdout.decode("utf-8-sig"))
        if not isinstance(body, dict):
            raise ValueError("Expected one JSON object")
        normalized = normalize(body, args.adapter, args.model, args.effort, args.task_id,
                               args.pool, record["elapsed_seconds"])
        (out / "answer.txt").write_text(normalized["reply"] or "", encoding="utf-8")
        write_json(out / "usage.json", {"entries": normalized["entries"],
            "coverage": "this_cli_call_only; coordinator and acceptance calls must be added separately"})
        record.update(models_reported=normalized["models_reported"], session_id=normalized["session_id"],
                      status="returned" if process.returncode == 0 and normalized["reply"] and
                      not normalized["provider_failed"] else "failed")
    except (ValueError, UnicodeError):
        record["status"] = "unparsed_response"
    if timed_out:
        record["status"] = "timed_out"
    record["automatic_retry"] = False
    write_json(out / "status.json", record)
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adapter", choices=("claude-code", "grok"), required=True)
    for name in ("executable", "workspace", "prompt-file", "output-dir"):
        parser.add_argument("--" + name, type=Path, required=True)
    for name in ("model", "task-id", "pool"):
        parser.add_argument("--" + name, required=True)
    parser.add_argument("--effort", choices=("low", "medium", "high"), default="low")
    parser.add_argument("--timeout", type=int, choices=range(1, 301), default=90, metavar="1..300")
    args = parser.parse_args()
    try:
        record = run(args)
        print(json.dumps(record, ensure_ascii=False, indent=2))
        return 0 if record["status"] == "returned" else 1
    except (ValueError, OSError) as exc:
        parser.exit(2, f"Dispatch input/output error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
