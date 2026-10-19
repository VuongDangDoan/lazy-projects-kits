# Implementation Pass — Shared Phase-4 Build Spec
> Followed by `/dev`, `/fe`, `/mobile`. Each command supplies the parameters in §0 and then
> executes this spec verbatim. Flow model: `.agents/orchestration.md` §1 Phase 4.
>
> **Inside this pass, steps chain automatically — no human stops between
> implement → typecheck → self-review → self-QC → fix. The single human gate is G4 at the end.**
> The only exceptions that stop the pass early: legacy gate failure, event/breaking-change
> gate failure, a SPEC defect, or a fix loop that needs a 4th round.

---

## 0. Parameters (supplied by the invoking command)

| Parameter | Meaning |
|---|---|
| `ROLE_FILE` | `.agents/roles/dev.md` \| `.agents/roles/fe-dev.md` \| `.agents/roles/mobile-dev.md` |
| `REPO_KEY` | `be` \| `fe` \| `mobile` — key under `repos` in `project.config.json` |
| `PATTERNS_FILE` | `knowledge/L0-global/be-patterns.md` \| `fe-patterns.md` \| `mobile-patterns.md` |

Resolve `REPO_NAME = repos.<REPO_KEY>.name` from `project.config.json`.
Never hard-code repo names, module lists, or stack specifics — the config and `PATTERNS_FILE` own those facts.

---

## 1. Pre-flight

1. Read `knowledge/L3-session/active-context.md` — SA decisions, legacy flag, constraints.
   **Missing-file branch:** if the file does not exist, tell the human:
   `active-context.md missing — run /switch-module [module] to initialize, or confirm I should proceed from the ticket alone.` Wait for the answer; do not silently proceed.
2. Read `tasks/tickets/[TICKET-ID].md` — primary input. No Acceptance Criteria → Phase 4 is blocked (orchestration §5); stop and route to `/planner`.
3. Read `ROLE_FILE` — agent identity and workflow.

On-demand only: api-contract yaml (when a field shape is unclear), legacy scan §7 Action Plan (when legacy flagged), `PATTERNS_FILE` sections, `.agents/contracts/doc-sync.schema.md`.

---

## 2. Gates — run in order, before writing any code

**Gate 0 — Layer match.** The ticket's `Layer` must include this command's layer
(`/dev` ↔ BE, `/fe` ↔ FE, `/mobile` ↔ MOBILE). Mismatch → print the correct command
(e.g. `This is a FE ticket — run /fe TICKET-NNN`) and stop.

**Gate 1 — Legacy freshness.** Run `scripts/legacy-scan-freshness.sh [module]`.
- `FRESH` (exit 0) → proceed.
- `STALE` (1) or `MISSING` (2) → **STOP.** Ask the human to run `/legacy-scan [module] [TICKET-ID]` (interactive ritual — cannot be automated). Never infer legacy behavior.
- Exception: ticket is pure net-new code with zero legacy intersection (confirm per the ticket's legacy flag) → note that and proceed.

**Gate 2 — API contract (FE / MOBILE tickets consuming endpoints).** The contract file
referenced by the ticket must exist under `architecture/api-contracts/v1/`.
Missing → **STOP**: `API contract not found — SA must complete it (Phase 2) before this layer builds.`

**Gate 3 — Event lock + breaking change** (orchestration §9.3, §10.3).
- Ticket involves an event → it must be **Locked** in `knowledge/L1-domain/module-integration-map.md`. Absent or Draft → **STOP**, escalate to `/sa`.
- Ticket `x-dev-notes.breaking_changes: "Yes — ..."` → an ADR with the Breaking Change Detail block must exist in `architecture/decisions/`. Missing → **STOP**, escalate to `/sa`.

---

## 3. Implement

Apply `ROLE_FILE`. Write the full ticket into `_source/<REPO_NAME>/` — never outside ticket scope.
Consult `PATTERNS_FILE` sections on demand for stack conventions. Layer-specific notes live in the invoking command file.

## 4. Typecheck gate

Run `scripts/typecheck-source.sh <REPO_NAME>`. Must pass before self-review.
Fails → fix and re-run; this is not a review finding, it is a precondition.

## 5. Self-review

Run the review spec in `.claude/commands/review.md` against your own diff (proportional tier
selection applies). It writes/appends `tasks/reviews/[TICKET-ID]-review.md` — one `## Round N` per pass.

## 6. Self-QC

Run the QC spec in `.claude/commands/qc.md` (per `.agents/roles/qc.md`): test cases per AC,
severity-scaled security review, executes runnable tests where a runner is configured.
QC appends its verdict to the review artifact.
Skip only under the Trivial protocol (orchestration §2.1 — review-only).

## 7. Fix loop

Classify every review/QC finding:
- **CODE defect** (bug, code-vs-contract mismatch, missing AC coverage) → fix directly, re-run steps 3–6. Each re-review appends a new Round to the artifact.
- **SPEC defect** (AC wrong, contract itself wrong, scope creep) → **STOP immediately**, escalate to the human. Spec work belongs to Phase 1/2 gates — never "fix" a requirement or contract yourself.

**Max 3 review rounds.** If a 4th round would be needed → **STOP**, escalate with the open findings. Do not wait for G4.

## 8. Doc Sync

Produce the plan per `.agents/contracts/doc-sync.schema.md`.
- **Auto-approve tier:** diff ≤ 20 lines AND no contract / domain / business-rule change → apply the propagation updates yourself and list them in the G4 report. No separate human stop.
- Otherwise → full Doc Sync Plan, held for human approval at G4. Apply only after approval.

## 9. Gate G4 — report and kanban

Update `tasks/kanban.md`: ticket → **In Review** (kanban ownership rule: the Build agent moves the ticket into In Review when posting the G4 report, and to **Done** only after the human approves).

Post the G4 report:

```
G4 — TICKET-NNN ready for review
1. Diff summary        — files changed + line counts, scope note
2. Review artifact     — tasks/reviews/TICKET-NNN-review.md — Round N VERDICT: PASS
3. QC verdict          — PASS/FAIL + tests/cases/[module]/TICKET-NNN-tests.md
4. Doc sync            — auto-applied: [list]  |  plan awaiting approval: [items]
5. E2E                 — mandatory ([trigger]) → next: /e2e-write TICKET-NNN
                         | not mandatory — [reason]
6. Suggested branch    — feat/TICKET-NNN-[slug]
   Commit message      — <type>(<scope>): <subject>   ← the HUMAN commits; agents never commit _source/
```

After human approval: apply approved doc updates (if any were held), move the ticket → **Done** on `tasks/kanban.md`.
