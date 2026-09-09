# Agent Brain for lowest budget and highest work efficiency

[简体中文](README.md) | **English**

A central coordination skill for Codex and other agents that support `SKILL.md`. Short name: **Agent Brain**.

Agent Brain assigns work according to each agent's capabilities and limitations, balancing cost and efficiency while meeting delivery requirements. The title describes an optimization goal, not a guarantee of mathematically minimal cost or maximal efficiency. Costs include the coordinator, workers, context transfer, acceptance checks, and retries. Simple tasks use one executor by default; delegation or parallel work is justified only when the benefits outweigh the overhead.

## What it does

- Builds a capability profile for each agent: suitable tasks, known limitations, tools and file access, execution channel, exact model, reasoning effort, and shared quota pool.
- Distinguishes Claude Haiku / Sonnet / Opus, Codex Luna / Terra / Sol, and available Google and Grok models. Model availability and capabilities come from the current environment.
- Provides a consistent workflow for dispatching tasks, collecting results, continuing sessions, and canceling work; unsupported operations are explicitly identified.
- Runs dependent tasks in order and parallelizes independent work when worthwhile. Separate workspaces prevent conflicting writes, and one integrator combines and validates results.
- Searches before reading relevant sections, filters verbose output, and preserves errors and retrievable original evidence.
- Uses concise task packets so each worker does not reread the entire conversation.
- Selects execution methods by capability and cost, and stops ineffective retries when quota exhaustion is confirmed.
- Separates cash spending, estimated costs, subscription quota, and time, without promising a fixed savings percentage.

This skill guides agent decisions. **It is not a dispatch service with all desktop applications already connected.** It does not independently install tools, create accounts, purchase credits, run background monitoring, or acquire additional permissions. Model capabilities, quotas, and billing rules must be verified in the actual environment; specific model generations and prices are not hardcoded.

## Installation and usage

Copy the `skills/agent-brain` folder into your Codex skills directory: `$CODEX_HOME/skills/agent-brain`, typically `~/.codex/skills/agent-brain` when `CODEX_HOME` is unset. For other clients, use their supported skill directory. Refresh the skill list or start a new session.

Example prompts:

> Use $agent-brain to complete this task. Compare the available agents' capabilities, limitations, and quotas, then assign a suitable executor. Add a complementary reviewer when useful, without enabling additional paid usage.

> Use $agent-brain to assess whether this multi-agent workflow was cost-effective. Distinguish actual usage, cost estimates, and components that have not been measured.

Load skill instructions as needed and consult the relevant references for routing, handoffs, or accounting. The 20% remaining-quota threshold is only a configurable starting suggestion, not an activated monitor.

## Validation scope

The skill format, relative links, and publication files were checked. An independent Luna worker also completed a decision evaluation covering six simulated dispatch scenarios. See the [evaluation scenarios](evaluations/scenarios.md) and [recorded results](evaluations/results.md). These checks do not establish an actual savings percentage or prove that an external application is connected.

## Sources and license

The content is an independently written synthesis of methods, without copying upstream implementations or substantial prompt text. See [sources and applicability limits](SOURCES.md) (Chinese). Original content in this repository is licensed under MIT; upstream projects retain their respective licenses.
