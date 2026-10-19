---
description: Proportional code review — trivial/standard/full tiers, stack-agnostic Security Gate, writes the review artifact
argument-hint: [TICKET-ID]
---

# /review — Code Review

Reviews the `_source/` diff for ticket `$ARGUMENTS`. This spec serves two callers:
- **Self-review step** inside the Phase 4 pass (`.agents/implementation-pass.md` §5) — runs automatically, no human stop.
- **Standalone** — human runs it manually at G4 or for a re-review after fixes.

Either way it appends a round to the review artifact (below). Resolve repo names from `project.config.json` — never hard-code them.

---

## Pre-flight

1. Read `tasks/tickets/$ARGUMENTS.md` — acceptance criteria + DoD.
2. Read the actual diff in `_source/<repo>/` for the changed repo(s).
3. Read `tasks/reviews/$ARGUMENTS-review.md` if it exists — prior rounds; this pass appends the next round.
4. Run `scripts/review-prep.sh <repo-name>` — aggregates typecheck + doc-sync diff + freshness drift. Exit 0 = OK, 1 = blocking gate failed, 2 = warnings only.
5. Run `scripts/typecheck-source.sh <repo-name>` — **BLOCKING**: static-analysis errors → write the round with VERDICT: FAIL immediately; do not continue the checklist. Judgment of code correctness is meaningless when the code does not compile.

On-demand only: api-contract yaml (contract field unclear); `knowledge/L2-legacy/scans/[module]-legacy-scan.md` (full tier with legacy touch).

## Skip Conditions

- **Safe to skip:** doc-only change with zero `_source/` diff (still verify the Doc Sync Plan was approved and applied).
- **Never skip:** any code change in any `_source/` repo — even one line; any change to api-contract yaml, db migrations, or state-machine docs; any legacy dual-write logic.

---

## Tier selection — proportional review

| Tier | When | Checks |
|---|---|---|
| **trivial** | diff ≤ 20 lines AND no behavior change | Trivial checklist only |
| **standard** | default — everything not trivial or full | Trivial + Standard checklist |
| **full** | legacy touch OR breaking change OR new endpoint OR auth/permission change | All + Security Gate + Legacy Safety |

When in doubt, go up a tier. Record the chosen tier in the review artifact.

### Trivial checklist (all tiers)

- [ ] Diff confined to the ticket's scope — no drive-by edits
- [ ] No secrets, credentials, tokens, or connection strings anywhere in the diff
- [ ] Comment hygiene (section below)
- [ ] Doc sync: auto-approve tier applied with listed updates, or a Doc Sync Plan exists

### Standard checklist (standard + full)

**Contract conformance**
- [ ] API response shape matches the yaml contract field by field
- [ ] All required request fields present and typed
- [ ] HTTP status codes and error response format match the contract

**Business rules**
- [ ] Every BR-ID referenced in the ticket is enforced in code
- [ ] State transitions go through a validation guard (per the layer's patterns file)
- [ ] Errors use the stack's standard error type per the patterns file §Errors; messages are human-readable and name the rule violated

**Error handling**
- [ ] No silent catch blocks — every failure surfaces to caller or user
- [ ] FE/Mobile: loading / empty / error states handled; mutations give success AND error feedback

**Tests & data safety**
- [ ] Test expectations in the ticket DoD are met (or QC cases cover them)
- [ ] Multi-table writes are transactional per the patterns file §Transactions
- [ ] Stack anti-patterns checked: be-patterns.md §12 / fe-patterns.md §15 / mobile-patterns.md §15 per ticket Layer — load the section, verify the diff violates none

### Full tier — Security Gate (stack-agnostic; failures are always Blocking)

- [ ] Authorization on every new/changed endpoint — authentication plus role/permission check at the boundary, not buried in a service
- [ ] Per-object access control — list/detail/update scoped to the caller's identity from the session, never from request params (no IDOR)
- [ ] Input validation at the boundary before any persistence or downstream call
- [ ] No raw SQL / string-built queries with user-controlled values — parameterized access only
- [ ] No secrets in code, committed config, or log output
- [ ] Error messages safe — no stack traces, internal paths, or query details reaching clients

Then: **run the stack-specific security checklist from the layer's patterns file §Security** (be-patterns.md / fe-patterns.md / mobile-patterns.md).

### Full tier — Legacy Safety (when legacy touched)

- [ ] Dual-writes are atomic — new and legacy writes both commit or both roll back, per the patterns file §Transactions
- [ ] Legacy column formats match legacy-scan §2; legacy response formats preserved on existing endpoints
- [ ] No legacy column or endpoint dropped, renamed, or type-changed without an ADR in `architecture/decisions/`
- [ ] External-system sync (if any) follows the conditions documented in the legacy scan §7 Action Plan

---

## Comment Hygiene (all tiers)

Concrete check — run against the diff:

```
git diff | grep -nE 'TICKET-|US-[0-9]|// (Step|Note:|This (function|method) )'
```

- [ ] No US-IDs, TICKET-IDs, AC-IDs, BR-IDs, or ADR-IDs in source comments
- [ ] No multi-paragraph file-header blocks summarizing the feature
- [ ] No comments narrating callers, lifecycle, or the current ticket flow
- [ ] Doc comments on public methods/hooks/components: at most ONE short line, only when the name alone isn't enough
- [ ] No inline comments restating the next line of code
- [ ] Exception: migration files may carry a 1–3 line factual header (what changed, why additive) with no ticket refs

Severity: **Minor** by default. Promote to **Blocking** only if comments leak business rules that belong in the domain doc, or every file carries the same boilerplate header (systemic regression).

## Doc Sync check (standard + full)

- [ ] The Build pass produced a Doc Sync Plan or an auto-applied list (`doc-sync.schema.md`)
- [ ] No stealth doc edits — every doc change in the diff matches a plan item or the auto-approve tier
- No plan and no auto-applied list at all → finding: Blocking / CODE — "Doc sync skipped; produce the plan before G4."

---

## Review artifact — MANDATORY output

Write or append `tasks/reviews/$ARGUMENTS-review.md`:

```
# Review — TICKET-NNN
## Round N — YYYY-MM-DD — VERDICT: PASS | FAIL
**Scope tier:** trivial | standard | full
**Gates:** typecheck PASS/FAIL · review-prep exit 0/1/2
| # | Severity | Type | File:Line | Issue | Resolution |
(Severity: Blocking/Major/Minor · Type: CODE or SPEC)
## QC — Round N — VERDICT: PASS | FAIL
(QC appends its verdict + pointer to test case file here)
```

Every finding is classified **CODE** (implementation wrong) or **SPEC** (the AC/contract itself is wrong, or scope creep). **Any SPEC finding stops the Phase-4 loop — escalate to the human immediately**; agents never fix requirements or contracts.

## Routing — which agent fixes which failure

| Failure type | Routes to |
|---|---|
| Code quality / logic / missing guard / wrong error type | `/dev`, `/fe`, or `/mobile` (per ticket Layer) |
| Code doesn't match contract | fix code — or `/sa` if the contract itself must change (SPEC) |
| Code enforces a BR not in `domain.md` §4 | `/sa` (or `/ba` if the rule was never agreed) — SPEC |
| New entity/endpoint invented without SA pass | `/sa` — SPEC |
| Missing Doc Sync Plan / plan approved but not applied | re-run the last Build pass |
| Missing test coverage for an AC | `/qc` |

**Rule of thumb:** code ≠ contract → fix code or `/sa`; code ≠ ticket → the Build agent; ticket/contract itself wrong → `/ba` or `/sa` (SPEC → escalate).

## Verdict

- **PASS** → the Phase-4 pass proceeds to self-QC (or, standalone: `next: /qc $ARGUMENTS`).
- **FAIL, CODE findings** → back to the implementing agent; fix loop, max 3 rounds (round 4 needed → escalate).
- **FAIL, any SPEC finding** → stop, escalate to human with the finding table.
