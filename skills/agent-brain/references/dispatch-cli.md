# Bounded CLI execution

Read when an authorized text task should actually run through Claude Code or
Grok CLI. Use `scripts/dispatch.py`, Python 3.10+, and an installed authenticated
CLI. On Windows provide the actual `.exe`; extension updates can invalidate paths
embedded in old `.cmd` wrappers. Resolve a current executable before a first call.

## Tell the user before calling

Name the model, channel, and concrete task in the user's language, then run it.
For example: “I'll ask Claude Code Sonnet to check the English instructions. I'll
read its findings and make the final changes.” If a retry changes the model,
announce the change first. Do not ask for another confirmation when the task is
already authorized. A Python status file is not a substitute for this notice.

## Execute one task

Prepare a UTF-8 prompt file containing the necessary text and acceptance request.
The executor has no tools, so include all input it needs. Create an empty or
otherwise appropriate workspace. Use a **new** task-local output directory for
each invocation. The following example paths must be replaced with real paths:

```sh
python scripts/dispatch.py --adapter claude-code --executable /path/to/claude --model sonnet --effort low --workspace work/isolated --prompt-file work/review.txt --output-dir work/run-001 --task-id review-english --pool verified-claude-pool
```

For Grok, use `--adapter grok`, its executable, and an available model identifier.
Both profiles restrict work to one text turn, disable model tools, and do not
automatically retry. The default timeout is 90 seconds (configurable up to 300).
Timeout cleanup targets the started process tree on Windows; elsewhere it kills
the direct CLI process, so descendant cleanup is not guaranteed. Provider-side
cancellation is not guaranteed. An uncertain cleanup must be investigated before
retrying. These are time/turn limits, not hard token or currency limits.

The executable's existing login/configuration is used. API-key environment
variables for these providers are removed from the child environment; the helper
does not buy credits, change account settings, or establish the billing mode.
Check the actual channel and existing spending authorization before dispatch.

## Read and accept the result

- `status.json`: adapter, requested model/effort, reported models, call state,
  time, process exit code, and session ID if provided.
- `answer.txt`: returned answer. The coordinator applies task acceptance checks.
- `usage.json`: normalized events suitable for `brain.py account`.
- `stdout.json` and `stderr.log`: raw provider output for diagnosis, kept local.

`returned` means a response was received, not accepted work. Report which models
actually participated, including auxiliary models when the provider exposes them.
An unresolved model alias is labeled `unresolved:`. Requested effort is recorded
as requested, not as a verified provider setting. Missing usage stays null.
Cost fields represent reported API-equivalent estimates, not subscription charges.
Add coordinator and acceptance usage separately to measure the complete workflow;
this adapter captures only its own CLI call.

If you use the deterministic planner first, map its selected model/channel/effort
and verified pool ID to these arguments, then dispatch. A direct explicit model
assignment can also run through this adapter after the coordinator checks it.
This helper does not discover quota, change the planner's evidence requirements,
or claim that a CLI session is the user's desktop app session.

Supported now: one-shot text tasks through Claude Code and Grok. Persistent resume,
file-editing tools, automatic quota retrieval, other providers, and desktop/browser
adapters remain separate integration work. Existing native Codex subagent tools
can still be used by the skill directly with the same advance-notice rule.
