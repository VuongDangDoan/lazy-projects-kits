# Active Context Schema v1.0
> Canonical shape of `knowledge/L3-session/active-context.md` — the single most-loaded file in the workspace.
> Every agent reads it at task start; whichever agent reaches an alignment milestone updates it.
> **Hard rule: ≤ 80 lines total.** Overflow → move detail to a per-feature companion file
> (`knowledge/L3-session/[feature]-context.md`) and reference it with one line.

---

## Required Sections (in order)

```markdown
# Active Session Context

## Session
| Field | Value |
|---|---|
| Project | [name from project.config.json] |
| Language | [vi | en | ...] |
| Phase / Gate | [Phase N — awaiting GN | idle] |
| Module | [module slug from project.config.json] |

## In Progress
- US: [US-NNN — title | None]
- Tickets: [TICKET-NNN (status), ... | None]

## Locked Decisions
> Append-only, one-liners. Never re-litigate; never delete within a session.
- [YYYY-MM-DD] [decision]

## Business Rules in Scope
**Business Rules in Scope:** [BR-IDs, comma-separated | None]
> Validated by `scripts/validate-active-context.py` against domain.md §4.

## Legacy
- Involved: [No | Yes — scan: knowledge/L2-legacy/scans/[module]-legacy-scan.md (fresh YYYY-MM-DD)]

## Do NOT
> Session-scoped prohibitions — things agents must not do this session.
- [prohibition | (none)]

## Last updated
| Date | Updated by | Trigger |
|---|---|---|
| YYYY-MM-DD | [agent] | [event] |
```

---

## Rules

- Sections may be empty ("None" / "(none)") but never absent.
- Locked Decisions is append-only — corrections are a new line, not an edit.
- The canonical **empty template** lives in `scripts/archive-active-context.sh --reset` —
  this schema and that script must stay in sync; change one, change both.
- `/switch-module` archives + resets the file via that script — agents never hand-roll a fresh template.
