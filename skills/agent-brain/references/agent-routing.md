# Capability-aware agent routing

Read when multiple agents could contribute or when a new execution channel must be assessed. Maintain a small task-local capability registry, not an exhaustive catalog or a public copy of private account data.

## A candidate is more than a model name

Record these facts only when relevant:

| Field | Meaning |
| --- | --- |
| channel / adapter | Native subagent tool, Claude Code CLI, Antigravity CLI, Grok CLI/ACP, desktop Chat/Cowork, browser Chat/Work, or API |
| exact model / effort | Current resolvable identifier; record aliases and what they actually resolved to |
| capabilities | Tools, modalities, browsing, project context, local-file access, supported run/resume/status/cancel actions |
| strengths / limitations | Task evidence and known restrictions; label untested role assignments as hypotheses |
| availability | Discovered, authenticated, response-tested, task-tested, blocked, or unknown; include observation time |
| quota / billing | Pool identity, remaining/reset when observable, source and freshness; distinguish subscription from API |
| performance | Accepted tasks, failures, wall time, reported usage and cost; avoid comparisons from unlike tasks |

Never treat Claude through Antigravity as the same billing channel as Claude Code. Never infer that models on one channel have separate pools. A website, desktop app, CLI, and API may share an account without sharing tools, memory, quotas, or sessions.

## Initial role hypotheses

These are configurable priors, not benchmarks or permanent rankings. Explicit user instructions and actual measurements take precedence.

| Candidate family | Initial assignment to consider | Check before assigning |
| --- | --- | --- |
| Codex Luna | Extraction, classification, bounded transformations and focused changes | Enough capability for the ambiguity; selected effort is supported |
| Codex Terra | General implementation and tasks requiring moderate judgment | Required tools and target files are accessible |
| Codex Sol | Difficult planning, complex debugging and ambiguous integration | Benefit over balanced models exceeds extra cost |
| Claude Haiku | Small clear operations, if available | Availability, required quality and actual model ID |
| Claude Sonnet | General coding, multi-file work and review | Required project context, permissions and quota |
| Claude Opus | Hard reasoning and complex reviews | Stronger analysis is useful; not a default second opinion |
| Gemini / Antigravity models | Document or multimodal analysis, research and coding depending on the actual model | Modality/tool support, context limits, exact model and the appropriate quota group |
| Grok models | Independent analysis or research when the appropriate tools are enabled | Browsing/X access is not implied by the brand or by a successful no-tool CLI probe |
| Desktop Chat / Cowork | Work requiring that app's project context, connectors or UI-only capabilities | Actual send-and-read-back test; login, app availability and permissions |
| Browser Chat | Self-contained text work when a distinct usable pool and reliable interaction are established | Correct mode and account; browser manipulation and acceptance overhead |

## Unified dispatch procedure

1. Extract the deliverable and required capabilities. Keep small mechanical tasks local when possible.
2. Select feasible candidates; exclude unavailable models, exhausted pools, unverified mandatory capabilities, and unauthorized channels. If none qualify, report the specific missing capability.
3. Select one executor by fit, evidence, remaining quota, estimated total cost, and latency. Do not pay for an additional model merely to choose a model when simple rules suffice.
4. Create the minimal task packet. For changes, specify file ownership or an isolated worktree. Preserve applicable repository instructions. Pass relevant facts rather than broad unrestricted access.
5. Use a real available native tool or documented CLI/ACP adapter. Consult local help for unsupported/changed flags. Retain the returned job/session ID and relevant paths. Use scoped permissions; do not default to approve-all flags. Do not equate a zero process exit code with a successful model result.
6. Read status through events or bounded polling. Respect dependencies. Support continuation and cancellation only if the adapter exposes them; handle pending external side effects before retries.
7. Require an answer/artifact plus relevant evidence. One integrator checks acceptance and conflicting edits. Escalate the missing capability or difficult subproblem rather than rerunning everything on every model.

For a read-only implementation plan, this procedure should produce a proposed dispatch, not execute modifications. For an authorized action, proceed through execution and acceptance rather than stopping at a routing table.

## Common decisions

- A desktop-only request is not satisfied by silently using a CLI. Explain an alternative when necessary, preserve completed independent work, and report what remains unsupported.
- A source-research worker can return cited findings to a coding worker; the coding worker need not repeat the research. A reviewer receives the diff and acceptance criteria, not every prior message.
- If a model returns good prose but the requested build fails, record the task as unaccepted. If two workers edit the same file, stop conflicting writes and let the integrator resolve them.
- Use prior task outcomes to adjust role preferences. A provider's marketing or one connection test is insufficient evidence of superiority.
