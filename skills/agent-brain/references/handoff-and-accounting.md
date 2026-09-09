# Handoff and accounting

Use only the fields needed by the task. Do not construct a large ledger for a one-step job.

## Minimal task packet

```text
Objective and acceptance:
Necessary facts and source/file references:
Allowed workspace/actions and restrictions:
Deliverable (result, changed files, evidence):
Timeout / turn limit supported by this interface:
When to stop and return a blocker:
```

A return packet should include status, result, evidence or changed paths, unresolved issues, and reported usage when available. A summary should retain completed work, current state, decisions, constraints, and next action; reference raw artifacts rather than repeating them. Do not include passwords, tokens, or unrelated private conversations in packets or published examples.

## Account for complete work

Track, when provided: task ID, channel, exact model, effort, quota-pool ID, timestamp, input/output/cache/reasoning tokens, latency, retries, and acceptance outcome. Preserve the provider's field meanings; missing values remain unknown.

- Separate cash paid, estimated token-priced cost, subscription quota consumption, and wall time. Do not add unlike units or compare providers by raw token totals alone.
- Include parent routing, worker startup/context, worker execution, result reading, verification, and failed attempts. Include embedded auxiliary-model calls when reported.
- For cumulative session counters, use consistent deltas; do not add cumulative totals repeatedly. Cached and reasoning tokens may already be included in other totals. Consult the relevant schema before arithmetic.
- A request deadline or maximum turn count is not a hard token or monetary cap. Label unsupported caps as advisory. Poll or use callbacks only as needed; frequent model-driven polling has its own cost.
- Quota snapshots may be affected by other sessions and coarse rounding. Attach freshness and uncertainty; do not attribute every before/after change to this task.

## Decide whether routing pays off

Use previous comparable completed tasks as a low-cost baseline. If that cannot answer a meaningful decision, run a small controlled comparison with the same inputs, acceptance criteria, and quality checks; include the comparison's own expense. Do not repeat an entire job solely to produce a savings headline.

Compare accepted outcomes, retries, latency, and observed cost in the same units. Only calculate savings when comparable costs are known and the baseline is nonzero. State sample size, cache state, model/effort, unknown accounting components, and quality limitations. A small pilot supports a local decision, not a universal guarantee.

If handoff overhead dominates, merge small related tasks, shorten packets, use a simpler route, or execute directly. If quality drops, restore the missing context or escalate the specific difficult part.
