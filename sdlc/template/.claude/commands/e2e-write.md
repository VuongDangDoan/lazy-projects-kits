---
description: Generate an E2E test case from a ticket — global TC-E-NNN ID, validated against the case schema
argument-hint: [TICKET-ID]
---

# /e2e-write — E2E Tester Agent (write mode)

Output: `tests/e2e/cases/<module>/TC-E-NNN-<slug>.md` (one file per AC scenario).
Does NOT run the case — use `/e2e TC-E-NNN` afterward.

Use when: a ticket with UI-visible behavior needs E2E coverage before merge; an existing case
failed as **Stale** and needs a refresh; a bug ticket needs a reproducing regression case.

## Layer gate

Read the ticket's `Layer`:
- **FE / BE+FE / MOBILE / MOBILE+BE** → E2E applies, proceed.
- **BE-only** → stop:
  ```
  E2E-write blocked: $ARGUMENTS is BE-only. E2E cases cover user-visible behaviour.
  For API-level coverage, add an integration test via /qc $ARGUMENTS instead.
  ```

## Pre-flight

Mandatory:
1. `tasks/tickets/$ARGUMENTS.md` — ACs + Layer
2. `.agents/contracts/e2e-case.schema.md` — output format
3. `.agents/roles/e2e.md` — Write mode workflow (Steps 1–5)

On-demand (may not exist yet — proceed without, and note the gap in the case's Preconditions):
- `architecture/feature-map/<module>.md` — confirm the page/screen exists, pick the route
- `knowledge/L1-domain/<module>-domain.summary.md` — business-rule context for failure hints

## ID assignment — global, script-owned

```
scripts/next-id.sh e2e
```

TC-E-NNN IDs are **global across modules** — official rule. Never eyeball the case directories
to pick a number; the script owns the sequence.

## Execution

Apply `.agents/roles/e2e.md` Write mode (Steps 1–5). Case header rules:
- `Owner: E2E Agent`
- Slug: lowercase, hyphenated, ≤ 6 words (e.g. `TC-E-014-create-order-happy-path.md`)
- Tag `regression` when the case guards a fixed bug or a critical path

**Validate before declaring done:** run `scripts/validate-e2e-case.py` on the new file and fix
any schema violations.

## Doc Sync

The case file is the primary artifact (no approval needed). Propagation:
- `tests/e2e/cases/_index.md` — add a row for the case
- `tests/regression-map.md` — add to the module's list if tagged `regression`

**Auto-approve tier applies** (per `.agents/implementation-pass.md` §8): these index-row updates
are ≤ 20 lines and touch no contract/domain/BR — apply them directly and list them in the handoff.
Anything beyond index rows → full Doc Sync Plan for human approval.

## Handoff Signal

```
E2E case written: TC-E-NNN
File: tests/e2e/cases/<module>/TC-E-NNN-<slug>.md
Validation: validate-e2e-case.py PASS
Doc sync (auto-applied): _index.md row[, regression-map row]

Run it: /e2e TC-E-NNN
```
