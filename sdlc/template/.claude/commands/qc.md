---
description: QC pass — test cases per AC, severity-scaled security review, verdict appended to the review artifact
argument-hint: [TICKET-ID]
---

# /qc — QC Agent

QC for ticket `$ARGUMENTS`. This spec serves two callers:
- **Self-QC step** inside the Phase 4 pass (`.agents/implementation-pass.md` §6) — runs automatically.
- **Standalone** — human runs it at G4 or to expand coverage on a shipped ticket.

---

## Gate — passing review round required

`tasks/reviews/$ARGUMENTS-review.md` must exist AND its latest `## Round N` verdict must be **PASS**.

- File missing → stop: `QC blocked: no review artifact. Run /review $ARGUMENTS first.`
- Latest round FAIL → stop: `QC blocked: latest review round is FAIL. Fix findings and re-review first.`

## Pre-flight (slim)

1. `knowledge/L3-session/active-context.md`
2. `tasks/tickets/$ARGUMENTS.md` — all ACs
3. `tests/regression-map.md` — regression scope
4. `tasks/reviews/$ARGUMENTS-review.md` — latest round (what review already covered)
5. `.agents/roles/qc.md` + `.agents/contracts/test-case.schema.md`

On-demand only:
- `architecture/db-schema/state-machines/[entity]-states.md` — entity has ≥3 states
- `knowledge/L2-legacy/scans/[module]-legacy-scan.md` — ticket has legacy flag
- api-contract yaml — a field shape is unclear from the ticket

---

## Execution

Apply `.agents/roles/qc.md`.

1. **Map every AC to test cases** per `test-case.schema.md` — no AC without at least one case.
2. **Scope by ticket Layer:**

   | Layer | Test scopes |
   |---|---|
   | BE | unit (business logic) · integration (API vs contract) · state transitions · legacy dual-write · regression |
   | FE | component/interaction · service/hook · UI state handling (loading/empty/error) · regression |
   | MOBILE | unit + state · integration against the api-contract · platform notes (offline behavior, permissions at point of use, secure storage of tokens/PII, deep links/navigation) · regression |

3. **Execute runnable tests when a runner exists.** Check `project.config.json` `repos.<key>.check_cmd` and `knowledge/L0-global/tech-stack.md` for a configured test command. If one exists, run the tests relevant to the ticket and record actual results in the case file. If none is configured, the cases are documentation for the human — mark them `not executed — no test runner configured`.
4. **Check the regression map** — list the regression cases that must run before merge.
5. **Security review — severity-scaled:**
   - **Full security table** (written to `tests/security/$ARGUMENTS-security.md`) only when the Layer includes BE, OR the ticket touches auth, permissions, or data handling.
   - Otherwise: a 3-line note **inside the test case file**: `Security review: N/A — <reason, e.g. presentational FE change, no data/auth surface>`.
6. **Validate the output:** run `scripts/validate-test-case.py` on the test case file; fix any schema violations before declaring done.
7. **Append the QC verdict to the review artifact** `tasks/reviews/$ARGUMENTS-review.md`, matching its format:

   ```
   ## QC — Round N — VERDICT: PASS | FAIL
   Test cases: tests/cases/[module]/$ARGUMENTS-tests.md
   [Security: tests/security/$ARGUMENTS-security.md | N/A — reason]
   Executed: [X/Y run, results] | not executed — no runner configured
   ```

## Output Location

```
tests/cases/[module]/[TICKET-ID]-tests.md
tests/security/[TICKET-ID]-security.md     (only when the full security table is triggered)
```

## Verdict

- **PASS** → the Phase-4 pass proceeds to Doc Sync + G4. Standalone: report ready for G4.
- **FAIL** → classify each finding:
  - **CODE** defect → back to the Build agent's fix loop (re-implement → re-review → re-QC; max 3 rounds).
  - **SPEC** defect (AC itself wrong, contract wrong, scope creep) → **stop, escalate to human immediately** — belongs to Phase 1/2.
