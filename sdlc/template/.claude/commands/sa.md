---
description: Phase 2 — Architecture. SA Agent designs API contract + entity design (+ state machine / ADR), stops at Gate G2.
argument-hint: [US-ID]
---

# /sa — Phase 2 · Architecture

Input: `docs/user-stories/$ARGUMENTS.md`

Flow reference: `.agents/orchestration.md` §1 Phase 2. Produces Phase 2 artifacts and stops at **Gate G2**.

---

## Pre-flight — mandatory

1. Read `knowledge/L3-session/active-context.md` — module, agreed approach, constraints.
   - **If missing:** recreate the fresh template (canonical in `scripts/archive-active-context.sh --reset`) or ask the human to run `/onboard` — never silently invent context.
2. Read `docs/user-stories/$ARGUMENTS.md` — SA Handoff Notes section first.
3. Read `project.config.json` — repo stacks, module list, `language`. Never hard-code repo or module names.
4. Read `architecture/feature-map.md` (index) → then `architecture/feature-map/[module].md`. Note: `architecture/feature-map/` is a directory of per-module files — SA **creates the module file on first touch** (and adds its row to the index). Load other modules' files only for in-scope cross-module touchpoints.
5. Read `.agents/roles/sa.md` — the role file owns the detailed steps.
6. Read `.agents/contracts/api-contract.schema.md` — output contract.
7. Read `.agents/contracts/doc-sync.schema.md` — for the secondary-doc sync plan.

## Pre-flight — on-demand only

- `knowledge/L0-global/naming-convention.md` / tech-stack — only when choosing entity names or patterns
- Domain file / `module-integration-map.md` — only for a specific BR or event lookup
- `.agents/contracts/adr.schema.md` — only when an ADR is triggered (new pattern/dependency, breaking change)
- If `active-context.md` shows `Legacy involved: Yes`: `knowledge/L2-legacy/scans/[module]-legacy-scan.md` (§7 first) + `_source/` read-only

---

## Execution

Follow the SA role flow from `.agents/roles/sa.md`. Command-level requirements:

1. Design API contract → `architecture/api-contracts/v1/[feature].yaml` with an `x-dev-notes` block.
2. Entity design → `architecture/db-schema/entities/[entity].entity.design.ts`.
   **SA does NOT write SQL migration files** — Dev generates migrations from the entity design via the stack's CLI in Phase 4.
3. State-machine doc `architecture/db-schema/state-machines/[entity]-states.md` — only if the entity has ≥3 states.
4. ADR — only when triggered. Allocate the ID via `scripts/next-id.sh adr` → `architecture/decisions/[NNN]-[title].md` per `adr.schema.md`.
5. New or changed event shape → lock it in `module-integration-map.md` before G2 (orchestration §9).
6. Validate: run `scripts/validate-api-contract.py architecture/api-contracts/v1/[feature].yaml` — must exit 0 before declaring done.
7. Doc Sync Plan per `doc-sync.schema.md` for secondary docs (feature-map, domain, integration-map) — STOP for human approval before writing them. Primary SA artifacts (yaml, entity design, state machine, ADR) are SA-owned and need no doc-sync approval.
8. Update `active-context.md` (SA Decisions) and the feature-map rows.

---

## Outputs

```
created:  architecture/api-contracts/v1/[feature].yaml        (with x-dev-notes)
          architecture/db-schema/entities/[entity].entity.design.ts
          architecture/db-schema/state-machines/[entity]-states.md   (only if ≥3 states)
          architecture/decisions/[NNN]-[title].md                    (only if ADR triggered)
updated:  knowledge/L3-session/active-context.md
          architecture/feature-map/[module].md (+ feature-map.md index)
```

---

## Gate G2 handoff

End the response with:

```
Phase 2 artifacts ready: [list].
validate-api-contract.py: PASS
Awaiting G2 approval. Next after approval: /planner US-NNN
```
