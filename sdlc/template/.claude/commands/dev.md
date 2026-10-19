---
description: Phase 4 Build pass for the backend layer — self-audit loop, single human gate at G4
argument-hint: [TICKET-ID]
---

# /dev — BE Dev Agent (Phase 4 Build)

Run the Phase 4 Build pass for the **backend** layer on ticket `$ARGUMENTS`.

| Parameter | Value |
|---|---|
| Role file | `.agents/roles/dev.md` |
| Repo key | `be` → `repos.be` in `project.config.json` (name, stack, check_cmd) |
| Patterns file | `knowledge/L0-global/be-patterns.md` |

**Follow `.agents/implementation-pass.md` exactly** — pre-flight, gates 0–3, implement,
typecheck, self-review, self-QC, fix loop, Doc Sync, G4 report, kanban updates.

## Layer notes (BE only)

- **Migrations:** SA delivers the entity design (`architecture/db-schema/entities/`); Dev
  generates the DB migration from it via the stack's own CLI (see be-patterns.md §Migrations).
  Never hand-write migration files when the stack has a generator.
- Stack conventions and anti-patterns: be-patterns.md §12 — load on demand; never assume a
  specific framework or ORM.
