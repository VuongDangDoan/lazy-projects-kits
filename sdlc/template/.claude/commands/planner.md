---
description: Phase 3 — Planning. Planner Agent splits the story into tickets, updates kanban, stops at Gate G3.
argument-hint: [US-ID]
---

# /planner — Phase 3 · Planning

Input: $ARGUMENTS

Flow reference: `.agents/orchestration.md` §1 Phase 3. Produces tickets and stops at **Gate G3**.

---

## Pre-flight (slim — matches `.agents/roles/planner.md`)

1. Read `knowledge/L3-session/active-context.md` — active module + SA decisions.
   - **If missing:** recreate the fresh template (canonical in `scripts/archive-active-context.sh --reset`) or ask the human to run `/onboard` — never silently invent context.
2. Read the `x-dev-notes` block of `architecture/api-contracts/v1/[feature].yaml` — this is the SA→Planner handoff. Do NOT re-read the full yaml or the US unless `x-dev-notes` is insufficient.
3. Read `tasks/kanban.md` — current board state.
4. Read `.agents/roles/planner.md` (detailed steps) + `.agents/contracts/task-ticket.schema.md` (output contract).

---

## Execution

Follow the Planner role flow from `.agents/roles/planner.md`. Command-level requirements:

1. Split the story into tickets — one per layer slice. `Layer` values: `BE | FE | MOBILE | BE+FE | MOBILE+BE`.
2. Allocate every ticket ID by running `scripts/next-id.sh ticket` — never scan the kanban or directories for the next number.
3. Write `tasks/tickets/TICKET-NNN.md` per `task-ticket.schema.md` — complexity with rationale + dependency order.
4. Update `tasks/kanban.md` — add all new tickets to "To Do".
5. Sprint file is OPTIONAL: create `tasks/sprints/sprint-N.md` only if the team uses sprints.
6. Validate: run `scripts/validate-ticket.py tasks/tickets/TICKET-NNN.md` on each ticket — must exit 0 before declaring done.

---

## Gate G3 handoff

End the response with:

```
Phase 3: [N] tickets ready.
  TICKET-NNN — [title] — [Layer] — [complexity]
  ...
Dependency order: TICKET-A → TICKET-B → ... (parallels noted)
validate-ticket.py: PASS (all tickets)
Awaiting G3 approval. Next after approval (per ticket Layer):
  /dev TICKET-NNN | /fe TICKET-NNN | /mobile TICKET-NNN
```
