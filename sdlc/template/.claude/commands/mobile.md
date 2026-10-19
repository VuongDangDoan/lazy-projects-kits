---
description: Phase 4 Build pass for the mobile layer — self-audit loop, single human gate at G4
argument-hint: [TICKET-ID]
---

# /mobile — Mobile Dev Agent (Phase 4 Build)

Run the Phase 4 Build pass for the **mobile** layer on ticket `$ARGUMENTS`.

| Parameter | Value |
|---|---|
| Role file | `.agents/roles/mobile-dev.md` |
| Repo key | `mobile` → `repos.mobile` in `project.config.json` (name, stack, check_cmd) |
| Patterns file | `knowledge/L0-global/mobile-patterns.md` |

**Follow `.agents/implementation-pass.md` exactly** — pre-flight, gates 0–3, implement,
typecheck, self-review, self-QC, fix loop, Doc Sync, G4 report, kanban updates.

## Layer notes (Mobile only)

- **API contract is the input:** Mobile consumes the contract, never invents endpoint shape.
  Gate 2 (contract exists under `architecture/api-contracts/v1/`) is a hard block — missing
  contract routes back to `/sa`.
- **Legacy scans target the mobile repo:** when Gate 1 requires a scan for a mobile ticket,
  `/legacy-scan` reads `_source/<repos.mobile.name>/` — not the BE repo.
- Stack conventions and anti-patterns: mobile-patterns.md §15 — load on demand; never assume
  React Native / Flutter / Swift / Kotlin specifics.
