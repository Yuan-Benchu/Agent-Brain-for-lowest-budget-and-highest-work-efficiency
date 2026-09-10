# CLI adapter validation — 2026-09-11

The coordinator announced both assignments before dispatch. The installed CLIs
ran one text-only README review each through `scripts/dispatch.py`, with tools
disabled, low requested effort, one turn, and a 60-second timeout.

| Assignment | Requested model | Models reported by the CLI | Outcome |
| --- | --- | --- | --- |
| Check English README execution claims | Claude Code `sonnet` | `claude-sonnet-5`, auxiliary `claude-haiku-4-5-20251001` | Returned review and per-model usage; coordinator added an actual dispatch example and clarified adapter scope |
| Check Chinese README capability wording | Grok `grok-4.6` | `grok-4.6-build` | Returned review and usage; coordinator separated workflow conventions from implemented resume/cancel capabilities |

The English reviewer lacked implementation files and could not independently
verify that dispatch code existed. Its ambiguity finding was addressed by linking
the implementation and showing its command, rather than treating the capability
as merely a design. The coordinator checked both reviews before adopting edits.

Raw prompts, replies, session identifiers, and account-specific records remain
local. Normalized usage records were generated automatically; unknown quantities
remain unknown. Provider API-equivalent cost estimates are not cash charges.
These records cover the CLI calls, not the coordinator's full conversation cost.

Offline suite: 23 tests across planning/accounting and CLI command construction,
model usage parsing, auxiliary-model separation, unknown fields, provider failure,
nonzero exits, raw evidence persistence, duplicate output-directory protection,
and timeout state. Command: `python -m unittest discover -s evaluations -p "test_*.py"`.

This validates two bounded text tasks. It does not validate all models, file
editing, desktop/browser control, persistent sessions, automatic quota discovery,
or a percentage cost reduction. Requested effort is recorded as requested;
internal effort for auxiliary calls was not independently observed.
