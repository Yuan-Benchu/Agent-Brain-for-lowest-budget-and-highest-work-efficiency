---
name: agent-brain
description: Coordinate multiple AI agents by capability, limitations, model, quota pool, and total task cost. Use for unified agent dispatch, complementary review, economical model selection, and concise handoffs; not every ordinary task needs orchestration.
---

# Agent Brain

Choose agents that can deliver the required result with acceptable quality, latency, and total cost. Exploit complementary capabilities without multiplying unnecessary calls. Preserve the user's chosen tools, scope, and authorization. This skill supplies operational decisions and bounded CLI helpers; it does not run a background scheduler.

## Dispatch by capability, not brand

Before starting work, tell the user in their language which model/channel will do which part and why, using one or two plain sentences. For example: “I'll use Claude Code Sonnet to check the English instructions, and Grok to check the Chinese instructions. I'll combine their findings.” State actual model identifiers when known; otherwise identify the current coordinator without inventing its model. Distinguish a proposed assignment from a completed call. Announce a model switch or added worker before it runs. This is a progress notice, not a new approval request; continue within existing authorization. Afterward, report which models actually ran and what they completed or failed to complete. If working directly without other models, say so briefly.

For concrete execution, read [operating-playbook.md](references/operating-playbook.md): task definition → eligible agent selection → minimal packet → actual dispatch → targeted repair → acceptance and accounting. Use `scripts/brain.py plan` for repeatable selection, `digest` for long local logs, and `account` for reported usage events. The helpers use the Python standard library and make no model calls; plan output is not execution. For authorized tasks, continue using the real available adapter after planning.

For one-shot text tasks through installed Claude Code or Grok CLI, read [dispatch-cli.md](references/dispatch-cli.md) and use `scripts/dispatch.py` to execute and capture results/usage. Announce the actual assignment first. These adapters disable tools; they do not implement desktop interaction, file editing, persistent resume, or automatic quota discovery. Use an available native adapter when those other capabilities are needed.

For multi-agent work or a new channel, read [agent-routing.md](references/agent-routing.md). Inventory each reachable executor's strengths, weaknesses, tools, data access, authentication, exact model, effort, quota pool, observed outcomes, and freshness. Treat model-family role suggestions as starting hypotheses; update them from actual accepted tasks.

Eliminate candidates missing required access, tools, quality, or authorization before comparing cost. Do not substitute a CLI for a requested desktop session, or an API for a subscription channel, without making that change explicit and respecting user intent. A model response test proves neither desktop access nor file-editing success.

Use the available adapter to submit a bounded task, retain its job/session ID, read results, and continue or cancel when supported. Normalize the task and result using [handoff-and-accounting.md](references/handoff-and-accounting.md). Report unsupported operations instead of inventing them. For dependencies, run in order; for independent work, isolate writable files/worktrees, then have one integrator resolve results and perform acceptance. Use a complementary reviewer only when its expected contribution warrants the cost.

## Choose the smallest useful workflow

- Use a deterministic command for mechanical work. Otherwise choose one executor first. Delegate only a bounded part whose expected benefit exceeds context transfer, startup, review, and retry overhead.
- Identify each candidate by **channel + exact model + effort + quota pool**. Desktop Chat, Cowork, CLI, web Chat, web Work, and API are separate entry points; neither equivalent capabilities nor independent quotas follow from their names.
- Resolve available models and authentication before a first dispatch. Reuse recent observations until expiry, configuration change, or failure. Distinguish listed, authenticated, response-tested, and task-tested capabilities.
- Respect an explicit model choice. Otherwise prefer an available economical model for clear tasks, a balanced model for judgment, and a stronger model for ambiguity or demonstrated failure. Start at the lowest suitable effort. Do not claim changing child models changes the current parent model.
- Prefer rules over an extra LLM routing call. Do not start agents solely to prove a connection already tested. Default to one worker; use at most two independent workers unless parallel benefit or the user justifies more. If delegation is unavailable, continue directly where the task permits; otherwise report the missing capability rather than pretending the requested agent participated.

## Control what gets read

- Search before reading. Select relevant files, sections, structured fields, and changed lines. Keep bulky raw outputs in task-local files and return compact summaries with retrieval paths.
- Preserve errors, exit codes, decisive evidence, exact identifiers, and user constraints when filtering. Reopen raw output if filtering may have hidden a cause. Never compress away an acceptance requirement.
- Prefer CLI/API and structured browser or accessibility state. Capture images when visual evidence is required or structured inspection fails; do not sacrifice correctness for a screenshot target.
- Give a worker the objective, necessary facts/files, allowed actions, deliverable, and acceptance check. Do not forward the full conversation by default. Independent context must still include all applicable constraints.
- Reuse a session for closely related steps when it reduces repeated context. For unrelated work, start fresh with a short state summary. Retain stable prefixes for caching; verify cache hits instead of assuming them.

## Bound failure and spending

- Read [handoff-and-accounting.md](references/handoff-and-accounting.md) only when delegating or measuring savings.
- At a confirmed quota exhaustion, stop that pool until its reset; do not cycle through models sharing it. Retry one transient failure after diagnosis. For an uncertain external mutation, inspect its outcome before any retry.
- Treat a 20% remaining-quota threshold as a configurable starting point, not an activated monitor. If relevant quota windows fall below it, consider another suitable, independently verified pool and reserve capacity for acceptance. Unknown quota is not zero. This skill never claims to run after its host stops.
- Do not enable paid overages, purchase credits, switch authentication to a paid API, or bypass service limits to keep a task moving. Existing explicit user authorization governs spending and external actions.
- Ask for one focused review only when the task warrants it. Do not create automatic chains of agent-to-agent reviews. Accept or diagnose using the requested checks, then stop.

## Report honestly

Separate successful invocation from successful work. Report the result, material limitations, and any observed usage relevant to the user. Do not promise a savings percentage from a compression ratio or count third-party estimated API prices as subscription charges.
