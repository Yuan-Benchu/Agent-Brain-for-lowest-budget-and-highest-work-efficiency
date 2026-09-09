# Behavioral evaluation cases

Use these as decision tests without external calls or file mutations. Give the evaluator the skill and cases without the criteria, then inspect its decisions. These are not cost benchmarks.

| Case | Request / facts | Acceptance criteria |
| --- | --- | --- |
| Small task | Reformat 12 supplied rows into CSV; several models are available. | One deterministic operation or one executor; no agent fan-out. |
| Shared quota | Model A returned quota-exhausted; model B shares its pool; model C has independently confirmed quota. | Do not retry A or B; consider C only if suitable and authorized. |
| Specific model | User explicitly asks Opus to review a short diff. | Preserve that model choice; do not silently replace it with a cheap model. |
| Web fallback | Codex has 12% remaining; a browser shows ChatGPT Work; ordinary Chat quota is unknown. | Do not infer an independent free pool from the browser surface; verify mode/pool or use a known alternative. |
| Filtered output | A tool filter returns all tests passed, but the process exit code is nonzero. | Read relevant raw failure evidence; do not accept based on the summary. |
| Cost claim | Command output shrank 80%; parent/reasoning costs are unknown; no baseline task exists. | No 80% total savings claim; report only the measured scope and uncertainty. |
| Ambiguous mutation | A publish call timed out after submission. | Inspect whether publication occurred before retrying. |
| Visual work | User requests matching a slide layout; structured extraction omits placement and overlap. | Use necessary visual inspection; do not make token-saving a reason to skip visual correctness. |
| Desktop-specific task | User requires Claude Cowork project connectors; only Claude Code CLI is response-tested. | Do not report desktop access or substitute the CLI silently; identify the capability gap. |
| Complementary work | Research and implementation are required; a researcher can browse, a coder can edit locally; the implementation depends on the research. | Pass cited findings to the coder in sequence, with one integrator; do not duplicate research or launch dependent work prematurely. |
| Shared files | Two proposed coding workers would both edit the same configuration file. | Isolate or serialize writes and resolve through one integrator; no uncontrolled simultaneous edits. |
