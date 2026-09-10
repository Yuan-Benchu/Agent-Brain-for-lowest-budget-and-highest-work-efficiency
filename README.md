# Agent Brain: lowest budget and highest work efficiency

**English** | [简体中文](README.zh-CN.md)

A central coordination skill for Codex and other agents that support `SKILL.md`. Short name: **Agent Brain**.

Our goal is to reduce quota consumption and completion time while meeting task quality requirements. Results vary with the task, models, and available quota. Costs include the coordinator, workers, context transfer, acceptance checks, and retries. Simple tasks use one executor by default; delegation or parallel work is justified only when the benefits outweigh the overhead.

## Our operating method

Before starting, the coordinator tells you in plain language **which model and channel will do what, and why**. It announces any added worker or model switch before dispatch, then reports what actually ran and what it completed. This is a progress update, not a repeated approval request. When it works directly, it says so rather than inventing a model identity.

The coordinator follows this workflow: **define delivery → select an executor → prepare a concise handoff → dispatch → repair the specific problem → accept and account**. The table describes the coordinator's responsibilities; `brain.py plan` only selects candidates. Procedures, input formats, and examples live in this repository; using the skill does not require reading upstream projects.

| Stage | Concrete action | Result |
| --- | --- | --- |
| Select | Check capabilities, channel, quality requirements, and shared quotas before comparing whole-task costs; use explicit preferences when costs are not comparable | Selected agent, model, channel, pool, and reasons for excluding alternatives |
| Prepare | Preserve objectives, acceptance, permissions, errors, and file scope; summarize successful logs and retrieve relevant code sections | An actionable task packet with retrievable original evidence |
| Dispatch | Feed research into implementation; sequence dependencies and isolate independent writes | Session IDs, execution state, file ownership, and returned results |
| Repair | Restore missing context, resolve access issues, or escalate only the subproblem that needs stronger reasoning | Completed work retained instead of restarting the entire task on a more expensive model |
| Accept and account | Check delivery, then account for coordination, execution, review, and retries; retain unknown measurements | Known consumption grouped by task, model, pool, and unit to inform future selection |

For a monetary rounding bug, send the failing example, relevant code, and allowed files to a suitable coding agent. Other agents need not participate. If a currency rule requires deeper reasoning, send that question and evidence to an appropriate model, return the finding to the implementation session, and have the coordinator check acceptance.

These procedures are implemented in the [skill instructions](skills/agent-brain/SKILL.md) and [operating playbook](skills/agent-brain/references/operating-playbook.md). Start with the [capability and limitation table](skills/agent-brain/references/agent-routing.md), then adjust assignments using actual task outcomes.

## Implemented local helpers

`brain.py` uses the Python 3.10+ standard library, requires no third-party dependencies, and makes no model requests. Run these commands from the repository root:

```sh
# Select from fictional profiles: returns demo-terra with exclusion reasons
python skills/agent-brain/scripts/brain.py plan skills/agent-brain/assets/demo.plan.json

# Account for fictional events: unknown costs stay null; models and pools stay separate
python skills/agent-brain/scripts/brain.py account skills/agent-brain/assets/demo.usage.json

# Extract evidence from an existing local UTF-8 log; replace 1 with its real exit code
python skills/agent-brain/scripts/brain.py digest work/raw.log --exit-code 1
```

The fixtures are offline examples, not evidence of real connections, capabilities, or remaining quota. For real work, the coordinator supplies verified channel observations and task requirements, runs selection, then dispatches through available agent tools. `plan` itself does not dispatch work.

The log helper returns a source path, hash, line numbers, exit state, and omission indicators. Incomplete failure evidence requires source review. Accounting rejects duplicate events, cumulative counters, and parent totals containing child calls. See the [playbook](skills/agent-brain/references/operating-playbook.md) for all three input contracts.

## What it does

- Executes bounded text tasks through installed Claude Code and Grok CLIs using `dispatch.py`, capturing responses and reported usage. These adapters do not expose file-editing tools, desktop control, or persistent resume. See [CLI dispatch](skills/agent-brain/references/dispatch-cli.md).
- Builds a capability profile for each agent: suitable tasks, known limitations, tools and file access, execution channel, exact model, reasoning effort, and shared quota pool.
- Distinguishes Claude Haiku / Sonnet / Opus, Codex Luna / Terra / Sol, and available Google and Grok models. Model availability and capabilities come from the current environment.
- Defines dispatch, result collection, continuation, and cancellation conventions for available host tools. The bundled CLI helper implements one-shot text execution and timeout cleanup; it does not implement persistent continuation or a general cancellation API.
- Runs dependent tasks in order and parallelizes independent work when worthwhile. Separate workspaces prevent conflicting writes, and one integrator combines and validates results.
- Searches before reading relevant sections, filters verbose output, and preserves errors and retrievable original evidence.
- Uses concise task packets so each worker does not reread the entire conversation.
- Selects execution methods by capability and cost, and stops ineffective retries when quota exhaustion is confirmed.
- Separates cash spending, estimated costs, subscription quota, and time, without promising a fixed savings percentage.

The skill includes dispatch instructions, local planning/accounting tools, and a CLI helper for one-shot text tasks. **Desktop connections, file-editing adapters, persistent resume, and automatic quota retrieval remain further work.** Model capabilities, quotas, and billing rules come from the actual environment.

## Installation and usage

To execute through the bundled adapter, prepare a UTF-8 prompt, an existing workspace, and the installed CLI's executable path. Replace the example executable below; use the actual `.exe` on Windows. The output directory must be new. The coordinator announces the model and assignment before running this command:

```sh
python skills/agent-brain/scripts/dispatch.py --adapter claude-code --executable /path/to/claude --model sonnet --effort low --workspace work/isolated --prompt-file work/review.txt --output-dir work/run-001 --task-id review-english --pool verified-claude-pool
```

This command actually calls the model and consumes its channel's allowance. It saves status, answer, raw output, and normalized usage in the output directory. For Grok, use `--adapter grok` with its executable and an available model. The [adapter guide](skills/agent-brain/references/dispatch-cli.md) explains setup and limits.

Copy the `skills/agent-brain` folder into your Codex skills directory: `$CODEX_HOME/skills/agent-brain`, typically `~/.codex/skills/agent-brain` when `CODEX_HOME` is unset. For other clients, use their supported skill directory. Refresh the skill list or start a new session.

Example prompts:

> Use $agent-brain to complete this task. Compare the available agents' capabilities, limitations, and quotas, then assign a suitable executor. Add a complementary reviewer when useful, without enabling additional paid usage.

> Use $agent-brain to assess whether this multi-agent workflow was cost-effective. Distinguish actual usage, cost estimates, and components that have not been measured.

Load skill instructions as needed and consult the relevant references for routing, handoffs, or accounting. The 20% remaining-quota threshold is only a configurable starting suggestion, not an activated monitor.

## Validation scope

The helper code includes 15 automated tests covering capability filtering, shared quotas, explicit model choices, stale observations, whole-task cost ranking, failure evidence, and duplicate accounting. Run `python evaluations/test_brain.py`. An independent Luna worker also completed six simulated dispatch decisions; see the [scenarios](evaluations/scenarios.md) and [evaluation record](evaluations/results.md). These check logic and behavior; actual savings require measurement on real tasks.

The CLI adapter adds 8 offline tests; run all 23 with `python -m unittest discover -s evaluations -p "test_*.py"`. Two real README review calls also returned results and usage through the adapter. See [CLI validation](evaluations/dispatch-results.md). These limited text-task checks do not establish desktop access or cost savings.

## Sources and license

The operating procedure, Python helpers, and tests were written for this project. [Design decisions and references](SOURCES.md) (Chinese) maps the ideas that informed specific implementations. Using this skill does not depend on those upstream projects. Original content is MIT licensed; upstream projects retain their respective licenses.
