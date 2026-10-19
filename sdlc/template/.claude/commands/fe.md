---
description: Phase 4 Build pass for the web frontend layer — self-audit loop, single human gate at G4
argument-hint: [TICKET-ID]
---

# /fe — FE Dev Agent (Phase 4 Build)

Run the Phase 4 Build pass for the **web frontend** layer on ticket `$ARGUMENTS`.

| Parameter | Value |
|---|---|
| Role file | `.agents/roles/fe-dev.md` |
| Repo key | `fe` → `repos.fe` in `project.config.json` (name, stack, check_cmd) |
| Patterns file | `knowledge/L0-global/fe-patterns.md` |

**Follow `.agents/implementation-pass.md` exactly** — pre-flight, gates 0–3, implement,
typecheck, self-review, self-QC, fix loop, Doc Sync, G4 report, kanban updates.

## Layer notes (FE only)

- **API contract is the input:** FE consumes the contract, never invents endpoint shape.
  Gate 2 (contract exists under `architecture/api-contracts/v1/`) is a hard block — missing
  contract routes back to `/sa`.
- Stack conventions and anti-patterns: fe-patterns.md §15 — load on demand; never assume a
  specific framework, styling system, or state library.
