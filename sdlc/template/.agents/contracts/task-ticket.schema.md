# Task Ticket Schema v2.0
> Planner Agent output MUST include every field below (Sprint and Assignee are optional).
> A ticket is the minimum context unit for the Build agent — it must be fully self-contained.
> ID: `TICKET-NNN` — global sequence via `scripts/next-id.sh ticket`, never hand-counted.
> **Status lives in this file.** `tasks/kanban.md` is a derived index of ticket statuses — the ticket file is the source of truth.

---

## Template

```markdown
# TICKET-[ID] — [Short Title]

**US-ID:** US-XXX
**Module:** [module slug from project.config.json]
**Layer:** [BE | FE | MOBILE | BE+FE | MOBILE+BE | BE+FE+MOBILE]
**Sprint:** Sprint-[N]                          # optional — omit if no sprint planning
**Assignee:** [Developer name | Unassigned]     # optional
**Status:** [Todo | In Progress | In Review | Done]
**Complexity:** [XXS | XS | S | M | L | XL]

---

## Task Description

[2–4 sentences describing exactly what this ticket does and why it is needed.]

---

## Input — Dev Agent must read

| Type | File | Notes |
|---|---|---|
| API Contract | `architecture/api-contracts/v1/[file].yaml` | Relevant endpoints: [list] |
| Entity Design | `architecture/db-schema/entities/[entity].entity.design.*` | Dev generates the migration from this via the stack CLI |
| Domain Knowledge | `knowledge/L1-domain/[module]-domain.md` | Section: [specific section] |
| Legacy Scan | `knowledge/L2-legacy/scans/[module]-legacy-scan.md` | [Required / Not required] |
| Business Rules | BR-[ID], BR-[ID] | |

---

## Acceptance Criteria

> Copied from US-XXX. Keep only the ACs relevant to this ticket.

**AC1:**
GIVEN [...]
WHEN [...]
THEN [...]

---

## Definition of Done

- [ ] Static-analysis gate passes (`scripts/typecheck-source.sh [repo]`)
- [ ] Tests for business logic per the stack's test runner, when one is configured
- [ ] API response matches contract in the yaml file
- [ ] Legacy endpoint not broken (if dual-write is involved)
- [ ] Migration (generated from entity design) runs without errors
- [ ] Review artifact final round PASS (`tasks/reviews/TICKET-[ID]-review.md`)

---

## Dependencies

**Must be completed first:**
- TICKET-[ID]: [reason]

**Can run in parallel:**
- TICKET-[ID]: [no conflict because...]

---

## SA Summary
> Copied from active-context SA Decisions by Planner. Makes this ticket self-contained.
> Dev reads this section instead of opening the full api-contract yaml.

**Endpoint(s) for this ticket:**
- `[METHOD] /v1/[resource]` — [purpose]

**New entities / columns:** [list or "None"]
**New npm dependencies:** [list or "None"]
**Legacy flag:** [No | Yes — table: [table_name], dual-write required: yes/no]
**State machine:** [None | [entity]-states.md]

---

## Dev Notes

[Gotchas, workarounds, or constraints the Planner wants Dev to know that are not in the SA Summary:
- Legacy column formats (e.g. WO-[YYYYMMDD]-[id])
- Temporary workarounds acceptable for this ticket
- Performance considerations]
```

---

## Validation Checklist — Planner self-checks before handoff

- [ ] Ticket ID is unique, format `TICKET-NNN`, obtained via `scripts/next-id.sh ticket`
- [ ] Module is a slug from `project.config.json` modules[]
- [ ] US-ID references a user story that actually exists
- [ ] Layer is one of: BE | FE | MOBILE | BE+FE | MOBILE+BE | BE+FE+MOBILE (matches `scripts/validate-ticket.py`)
- [ ] Input section is complete enough that Dev/FE Dev needs no follow-up
- [ ] ACs are copied accurately from the US — content not altered
- [ ] Dependencies checked — no circular dependencies created
- [ ] Complexity aligns with US estimate (or smaller with a stated reason)
- [ ] BE and FE work split into separate tickets when they can be parallelized

---

## Valid Example

> See `examples/task-ticket.example.md` for a fully filled example. Load it only when you need to anchor on format.
