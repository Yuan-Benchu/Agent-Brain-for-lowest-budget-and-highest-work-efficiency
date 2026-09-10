"""Local decision, evidence, and accounting helpers; Python 3.10+, no dependencies.

Inputs are explicit local JSON/log files. This module never calls an AI, runs a
shell command, edits a project, or discovers credentials. Outputs go to stdout.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re


def number(value):
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def fresh(item, now):
    try:
        expiry = datetime.fromisoformat(item["valid_until"].replace("Z", "+00:00"))
        return expiry.tzinfo is not None and expiry > now
    except (KeyError, ValueError, TypeError, AttributeError):
        return False


def plan(data, now=None):
    """Filter by verified ability, then compare whole-task estimates or priors."""
    now = now or datetime.now(timezone.utc)
    task, pools = data["task"], data["pools"]
    required = set(task.get("requires", []))
    min_tier = task.get("min_tier", 1)
    if type(min_tier) is not int or min_tier not in (1, 2, 3):
        raise ValueError("min_tier must be 1, 2, or 3")
    reserve = data.get("reserve_percent", 20)
    if not number(reserve) or reserve > 100:
        raise ValueError("reserve_percent must be between 0 and 100")
    ids = [a["id"] for a in data["agents"]]
    if len(ids) != len(set(ids)):
        raise ValueError("agent IDs must be unique")
    eligible, rejected = [], []
    for agent in data["agents"]:
        reasons = []
        if agent.get("authorized") is not True:
            reasons.append("channel_not_authorized")
        if agent.get("status") != "task-tested" or not fresh(agent, now):
            reasons.append("capability_evidence_missing_or_stale")
        missing = sorted(required - set(agent.get("capabilities", [])))
        if missing:
            reasons.append("missing_capabilities:" + ",".join(missing))
        if task["type"] not in agent.get("task_types", []):
            reasons.append("task_type_not_supported")
        tier = agent.get("tier")
        if type(tier) is not int or tier not in (1, 2, 3) or tier < min_tier:
            reasons.append("below_required_quality_tier")
        for field in ("agent", "model", "channel"):
            actual = agent.get("id" if field == "agent" else field)
            if task.get("requested_" + field) and task["requested_" + field] != actual:
                reasons.append("explicit_" + field + "_mismatch")
        pool = pools.get(agent.get("pool"), {})
        if pool.get("identity_verified") is not True:
            reasons.append("shared_pool_identity_unverified")
        remaining = pool.get("remaining_percent")
        if not fresh(pool, now) or not number(remaining) or remaining > 100:
            reasons.append("quota_unknown_or_stale")
        elif remaining == 0:
            reasons.append("shared_pool_exhausted")
        if pool.get("blocked") is True:
            reasons.append("pool_blocked")
        if not number(agent.get("preference_rank")):
            reasons.append("preference_rank_missing")
        if reasons:
            rejected.append({"agent": agent["id"], "reasons": reasons})
        else:
            eligible.append(agent)
    result = {"status": "blocked", "selected": None, "rejected": rejected,
              "dispatch_performed": False}
    if not eligible:
        return result
    # A requested model/channel has already constrained the candidate set.
    above_reserve = [a for a in eligible if pools[a["pool"]]["remaining_percent"] >= reserve]
    candidates = above_reserve or eligible
    result["deferred_low_reserve"] = [a["id"] for a in eligible if a not in candidates]
    estimates = [a.get("estimated_total", {}) for a in candidates]
    comparable = all(isinstance(e, dict) and number(e.get("value"))
                     and isinstance(e.get("unit"), str) and e["unit"] for e in estimates)
    comparable = comparable and len({e["unit"] for e in estimates}) == 1
    if comparable:
        candidates.sort(key=lambda a: (a["estimated_total"]["value"], a["preference_rank"], a["id"]))
        basis = "comparable_whole_task_estimates"
    else:
        candidates.sort(key=lambda a: (a["preference_rank"], a["id"]))
        basis = "configured_preference_cost_comparison_unavailable"
    chosen = candidates[0]
    result.update(status="planned", selected={k: chosen[k] for k in
                  ("id", "channel", "model", "effort", "pool")}, ranking_basis=basis,
                  reserve_warning=not bool(above_reserve))
    return result


def digest(path, exit_code, max_lines=60, max_chars=12000):
    """Produce a bounded, traceable excerpt, never an inferred acceptance result."""
    if max_lines < 1 or max_chars < 1:
        raise ValueError("excerpt budgets must be positive")
    path = Path(path).resolve()
    raw = path.read_bytes()
    lines = raw.decode("utf-8", errors="replace").splitlines()
    hits = [i for i, line in enumerate(lines)
            if re.search(r"error|fail|exception|traceback|fatal|错误|失败", line, re.I)]
    order = list(hits)
    for i in hits:
        order.extend(range(max(0, i - 2), min(len(lines), i + 3)))
    order.extend(range(min(3, len(lines))))
    order.extend(range(max(0, len(lines) - 3), len(lines)))
    chosen, chars, partial = {}, 0, False
    for i in dict.fromkeys(order):
        if len(chosen) >= max_lines or chars >= max_chars:
            break
        text = lines[i][:max_chars - chars]
        partial |= len(text) < len(lines[i])
        chosen[i] = text
        chars += len(text)
    return {"source": str(path), "sha256": hashlib.sha256(raw).hexdigest(),
            "exit_code": exit_code, "command_state": "failed" if exit_code else "exited_zero",
            "acceptance": "not_determined", "total_lines": len(lines),
            "needs_source_review": bool(exit_code) and (not hits or partial or len(chosen) < len(lines)),
            "omitted_lines": len(lines) - len(chosen), "partial_line": partial,
            "truncated": partial or len(chosen) < len(lines),
            "lines": [{"line": i + 1, "text": chosen[i]} for i in sorted(chosen)]}


def account(data):
    """Aggregate reported per-call deltas, keeping models, pools and units separate."""
    groups, seen, phases = {}, set(), set()
    for entry in data["entries"]:
        key_id = (entry["task_id"], entry["event_id"])
        if key_id in seen:
            raise ValueError("duplicate task/event ID; refusing possible double-counting")
        seen.add(key_id)
        if entry.get("counter_mode") != "delta":
            raise ValueError("convert cumulative counters to deltas before accounting")
        if entry.get("scope") != "own_call":
            raise ValueError("only own_call events are accepted; exclude parent/child aggregates")
        phases.add(entry["phase"])
        if not entry.get("metrics"):
            raise ValueError("declare expected metrics; use null for unknown values")
        for name, metric in entry["metrics"].items():
            key = (entry["task_id"], entry["agent"], entry["pool"], name, metric["unit"])
            row = groups.setdefault(key, {"task_id": key[0], "agent": key[1], "pool": key[2],
                "metric": name, "unit": key[4], "known_subtotal": 0,
                "reported_values": 0, "unknown_values": 0})
            value = metric["value"]
            if value is None:
                row["unknown_values"] += 1
            elif number(value):
                row["known_subtotal"] += value
                row["reported_values"] += 1
            else:
                raise ValueError("measurement must be nonnegative finite number or null")
    rows = list(groups.values())
    for row in rows:
        if row["reported_values"] == 0:
            row["known_subtotal"] = None
    return {"groups": rows, "phases_present": sorted(phases), "events": len(seen),
            "coverage": "provided_events_only", "savings_percent": None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("plan", "account"):
        sub.add_parser(name).add_argument("input", type=Path)
    log = sub.add_parser("digest")
    log.add_argument("input", type=Path)
    log.add_argument("--exit-code", type=int, required=True)
    log.add_argument("--max-lines", type=int, default=60)
    log.add_argument("--max-chars", type=int, default=12000)
    args = parser.parse_args()
    try:
        if args.command == "digest":
            result = digest(args.input, args.exit_code, args.max_lines, args.max_chars)
        else:
            data = json.loads(args.input.read_text(encoding="utf-8-sig"))
            result = {"plan": plan, "account": account}[args.command](data)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    except (ValueError, KeyError, TypeError, OSError) as exc:
        parser.exit(2, f"Invalid input: {exc}\n")


if __name__ == "__main__":
    main()
