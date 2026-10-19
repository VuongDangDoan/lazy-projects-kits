---
description: Run E2E test case(s) against the live system via Playwright MCP — Phase 5, Gate G5
argument-hint: <TC-E-ID> [--env=local|staging] [--browser=chromium|firefox|webkit] | --module <module> | --tag <tag>
---

# /e2e — E2E Tester Agent (run mode)

Output: `tests/e2e/results/<YYYY-MM-DD>/<run-id>/result.md` + screenshots

## Invocation

| Form | Behaviour |
|---|---|
| `/e2e TC-E-001` | Run one case against `env.json` default (local), chromium |
| `/e2e TC-E-001 --env=staging` | Run against staging |
| `/e2e TC-E-001 --browser=firefox` | Override browser (must be supported by the Playwright MCP install) |
| `/e2e --module <module>` | Run every case under `tests/e2e/cases/<module>/` (sequential; module names from `project.config.json`) |
| `/e2e --tag <tag>` | Run every case tagged `<tag>` across all modules |

## Pre-flight Checklist

1. Read `.agents/roles/e2e.md` — agent identity + Run mode workflow
2. Read `.agents/contracts/e2e-case.schema.md` and `e2e-result.schema.md`
3. Verify `tests/e2e/fixtures/env.json` exists and defines the requested env
4. Verify `tests/e2e/fixtures/test-users.json` exists.
   **Missing but `test-users.example.json` exists → do not dead-end.** Offer:
   ```
   test-users.json is missing. I can copy test-users.example.json → test-users.json now.
   You must then fill in real credentials for [env] before any run can log in.
   Copy it? (Runs stop here until credentials are filled.)
   ```
   Copy on approval, then STOP for the human to fill credentials.
5. Verify Playwright MCP is connected (`mcp__playwright__*` tools available)

Any other pre-flight failure → output the BLOCKED signal and stop.

## Batch guard

`--module` / `--tag` resolving to **more than 10 cases** → confirm with the human before starting
(list the count and case IDs; large batches are slow and burn env state).

## Execution

Apply `.agents/roles/e2e.md`, Run mode (Steps 1–8).

Multi-case runs (`--module` / `--tag`):
- Sequential, one case at a time — no parallelism (too easy to flake)
- Continue on FAIL — record every result, never stop the batch
- End with a summary: `<P>/<N> passed; failures: TC-E-XXX, TC-E-YYY`

**Flaky handling — executable step:** on the **first FAIL of a step, re-run the whole case once**.
Second run passes → record PASS with a `flaky` note in the result. Failure persists → classify **Bug**.

## Output Location

```
tests/e2e/results/<YYYY-MM-DD>/<run-id>/
├── result.md
├── screenshots/01-<slug>.png …
└── dom-at-failure.txt          (only if FAIL)
```

`<run-id>` = `<TC-E-ID>-<HHMMSS>` — repeat runs get their own directory, never overwrite.

## Handoff Signal

### PASS
```
E2E PASS — TC-E-NNN
Result: tests/e2e/results/<date>/<run-id>/result.md
Gate G5: verdict PASS — ticket can close.
```

### FAIL — classify and route
```
E2E FAIL — TC-E-NNN at Step <#>
Category: Bug | Stale | Environment | Flaky
Result: tests/e2e/results/<date>/<run-id>/result.md

Next action:
  - Bug         → back to Phase 4 on the SAME ticket (/dev | /fe | /mobile TICKET-NNN);
                  bug detail is in result.md §3
  - Stale       → /e2e-write TICKET-NNN to refresh the case, then re-run
  - Environment → fix env per result.md §3, then re-run
  - Flaky       → already re-run once automatically; if it persisted, it was classified Bug
```

### BLOCKED
```
E2E BLOCKED — TC-E-NNN
Reason: <from result.md> · Resolution: <from result.md>
Fix the blocker and re-run.
```
