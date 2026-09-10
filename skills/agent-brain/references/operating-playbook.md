# Agent Brain operating procedure

Use this reference to turn a task into actual work, especially for the first task
in a project. No upstream repository is required to follow this procedure.
The coordinator executes the workflow with available tools. `brain.py` computes
decisions and excerpts locally. For actual one-shot Claude Code or Grok text
execution, use `dispatch.py` as described in [dispatch-cli.md](dispatch-cli.md).

## 1. Define the job before selecting a model

Write one task record: objective, acceptance checks, task type, required tools or
connectors, allowed files, explicit model/channel choices, and dependencies.
For example, “fix checkout rounding; regression example must pass; only change
checkout code” is enough to route. A vague “improve the project” is not.

Use a deterministic command for mechanical transformations when feasible. For an
AI task, set the minimum acceptable tier for this task type: 1 = clear bounded
work, 2 = several interacting changes, 3 = unresolved ambiguity or difficult
reasoning. These are operator assessments, not universal model rankings.

## 2. Choose an executor with an explainable decision

Maintain only relevant candidates using the fields in [agent-routing.md](agent-routing.md).
Assign separate IDs to Sonnet and Opus, and to Claude Code and desktop Cowork.
Record capabilities from evidence: `local-edit`, `web-research`, or a specific
connector such as `cowork-drive`. Record observed limitations by omitting
unsupported capabilities/task types and lowering the task-specific tier. Store
the reason and evidence path alongside the profile for human inspection.

For a repeat decision, `python scripts/brain.py plan job.json` applies this order:

1. Reject unauthorized channels, missing required capabilities, unsupported task
   types, insufficient configured tiers, stale or untested capability records,
   unknown/stale quotas, blocked pools, and exhausted shared pools.
2. Apply explicit model, agent, or channel choices as constraints.
3. Prefer qualifying candidates above the configured reserve, within those
   constraints. If every candidate is below reserve, return a reserve warning.
4. Compare estimated **whole-task** consumption only when every remaining
   candidate has a nonnegative estimate in the same meaningful unit. Otherwise
   use the operator's `preference_rank`, and say that costs were not comparable.

This conservative helper requires `task-tested` evidence and `valid_until`
timestamps with timezone offsets. Missing evidence means “needs assessment,”
not “incapable.” Reuse actual recent task results; do not spend tokens on repeated
probes. Refresh only the missing observation through an authorized, useful task
or a read-only status query. Choose evidence expiry according to volatility;
quota observations usually need shorter lifetimes than stable tool support.

The JSON root has `task`, `agents`, `pools`, and optional `reserve_percent`.
Each agent includes `id`, `channel`, `model`, `effort`, `pool`, `authorized`,
`status`, `valid_until`, `capabilities`, `task_types`, `tier`, and
`preference_rank`. `estimated_total` is optional (`value`, `unit`). Each pool
has `remaining_percent`, `valid_until`, `identity_verified: true`, and optional
`blocked`. Pool keys must be canonical identities verified from the channel's
actual quota information; use the same key for models sharing a pool. A model
name or a different alias is not evidence of an independent pool. The helper
cannot detect falsely supplied identity claims. The task has
`type`, `requires`, `min_tier` and optional `requested_agent`, `requested_model`,
`requested_channel`. See the runnable [fictional input](../assets/demo.plan.json).

For estimates, include coordinator input, worker context, execution, result
reading, acceptance, and likely rework. Do not call provider-A credits and
provider-B credits the same unit. Use a qualified unit such as `codex-credit`;
use `USD` only for genuinely comparable monetary estimates with the same scope.
Never fill missing estimates with zero. For example, a cheap attempt costing 2
units plus an observed 50% chance of an 8-unit retry estimates 6 units, which
can lose to a reliable 5-unit route. Those numbers must come from comparable
work, not assumptions about a brand.

## 3. Build a small handoff that retains what matters

Keep a task-local `work/` directory with the task record, raw evidence, current
state, and usage events. Follow the user's workspace location when specified.
Do not send that entire directory to every agent.

Construct the packet in this order:

1. Preserve the objective, exact acceptance criteria, permissions, unresolved
   blockers, identifiers, and file ownership unchanged.
2. Include only facts and code sections needed for the assigned part. Reference
   other files by path and relevant lines, with a reason to retrieve them.
3. Replace repeated successful command output with a count and evidence path.
   Keep failures, exit codes, and the relevant surrounding context.
4. Remove superseded plans and repeated explanations. Preserve the current
   decision and any abandoned approach that prevents repeating a known failure.
5. Check that the worker can identify what to do, what it may change, and how
   completion will be judged. Restore missing context before dispatch.

Use `python scripts/brain.py digest raw.log --exit-code 1` on an existing UTF-8
log. It selects error-keyword lines and their neighbors, then opening/closing
lines. It emits line numbers, a source hash, exit state, and omission indicators.
The excerpt defaults to 60 lines / 12,000 content characters. This is heuristic
selection, not semantic compression or a tokenizer. Metadata adds overhead;
short logs often need no helper. It does not redact secrets, so keep logs local
and inspect content before any authorized external handoff. If evidence is
missing or contradictory, reopen the source at the relevant lines. A zero exit
code does not establish acceptance. For a nonzero exit with incomplete excerpts
or no recognized failure keywords, `needs_source_review` is true. Inspect the
original source before diagnosing; a keyword filter cannot identify every cause.

## 4. Run the work through the actual available channel

Before each new assignment or model switch, tell the user which model/channel
will do which part and why, using plain language. This is an advance progress
notice, not repeated permission-seeking for already authorized work. Report the
actual participating models and outcome afterward.

Map the packet to the host's native subagent tool or the installed CLI/ACP's
documented prompt input. Preserve the selected channel, model, effort and
workspace. Store the returned session/job ID, evidence paths, and whether the
interface supports status, continuation, or cancellation. Keep command arguments
structured; never execute shell text taken from the registry or model output.

Use this lifecycle: `planned → running → returned → accepted`, with `blocked`
or `failed` when appropriate. A returned answer is not yet accepted. A timed-out
call may still be running: inspect status or cancel when supported before
resubmitting. If status is unavailable after a side effect, report uncertainty.

Run research before implementation when the latter depends on the findings.
Independent components may run concurrently with separate file ownership or
worktrees. One integrator checks results; do not fan out the entire task to every
model or automatically ask all models to review each other.

## 5. Repair the actual cause, then escalate only if needed

| Observation | Next action |
| --- | --- |
| Missing file, connector, or permission | Fix access within authorization; a larger model cannot supply it |
| Exhausted quota | Block the shared pool; select another eligible pool or wait for reset |
| Transient service failure | Diagnose and retry once; retain a still-running job rather than duplicating it |
| Worker misunderstood an omitted requirement | Restore that requirement in the same task/session when possible |
| Required reasoning still fails after a focused repair | Escalate the unresolved subproblem with the failing evidence |
| Result meets acceptance | Record the result and stop |

For the next comparable task, update the candidate's task-specific fit and total
cost estimate from the outcome. Record sample count and reasons. One failure
does not establish a permanent ranking, and a connection test is not a benchmark.

## 6. Count complete work without mixing units

Record one uniquely identified event per task and call, including coordinator,
worker, reviewer, retry, and auxiliary-model work when reported. Represent
unavailable measurements explicitly as null. Convert cumulative session counters
to deltas before adding events; do not add a parent aggregate and its child
components twice.

Run `python scripts/brain.py account usage.json`. Each entry in `entries` has
`task_id`, `event_id`, `phase`, `agent`, `pool`, `counter_mode: "delta"`,
`scope: "own_call"`, and
`metrics`, where every metric is `{ "value": number-or-null, "unit": "..." }`.
Include channel, exact model, and effort in `agent` or use an ID that uniquely
maps to them. The output groups by task, agent, pool, metric, and unit, rejects
duplicate event IDs, retains unknown counts, and reports known subtotals only.
Parent totals that include worker calls are not own-call events and are rejected.
The coordinator's own model call can still be included. The helper relies on
truthful scope labels and cannot infer overlap hidden in mislabeled inputs.
It summarizes provided events; it does not automatically read provider logs or
detect omitted calls. See [example events](../assets/demo.usage.json).

Compare with existing accepted tasks of similar scope before running extra
benchmarks. Report observed consumption and quality together. When overhead
dominates, combine small jobs or use one executor next time. When rework dominates,
improve the packet or start with a more suitable model.

## Worked dispatch

Task: repair a rounding bug and explain it. Evidence: one failing regression,
three relevant files, no browsing required. Choose a capable coding executor
from current profiles; send the regression, relevant code, write scope, and
acceptance command. Keep unrelated research agents idle. If the repair passes,
one integrator reads the diff and checks the regression. If it fails because
currency conversion requirements are unclear, send only that unresolved question
and evidence to an appropriate stronger model, then return its finding to the
implementation session. Record all of those calls in the same task's accounting.
