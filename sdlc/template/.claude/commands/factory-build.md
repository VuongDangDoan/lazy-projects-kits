# /factory-build — Phase 4 Build of every open ticket (Lazy Bot factory)

Context from the owner: $ARGUMENTS

Run the Build phase for **all tickets still `Todo` or `In Progress`** in `tasks/kanban.md`, one at a
time, in ticket-ID order (respect each ticket's **Dependencies** first).

For each ticket:
1. Pick the layer from the ticket (`Layer:`) and follow the matching pass exactly as the command
   would: BE → `.claude/commands/dev.md`, FE → `.claude/commands/fe.md`, MOBILE →
   `.claude/commands/mobile.md` (all of them follow `.agents/implementation-pass.md`: implement →
   self-review → self-QC → fix loop, max 3 rounds, Doc Sync Plan).
2. Write the code under `_source/<repo>/` as configured in `project.config.json`.
3. Set the ticket's `**Status:**` to `Done` and move it to Done in `tasks/kanban.md` only when its
   self-review artifact in `tasks/reviews/` says PASS.
4. Update `knowledge/L3-session/active-context.md` (current ticket, what is left) before starting
   the next ticket — a new session may continue from there.

Stop conditions:
- A **SPEC defect** (wrong AC or contract): do not patch around it — call the factory MCP tool
  `ask_human` with the exact question, then continue with the answer.
- When every ticket is Done and `scripts/typecheck-source.sh` passes: call `stage_done` with the
  list of tickets done and the review verdicts. This is gate G4 — the owner reviews the PR.
