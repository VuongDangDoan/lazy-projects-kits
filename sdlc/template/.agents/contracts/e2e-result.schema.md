# E2E Run Result Schema v1.0
> Output of every `/e2e TC-E-XXX` run.
> Written by the E2E Tester Agent — never edited by hand.

---

## File Location

`tests/e2e/results/<YYYY-MM-DD>/<run-id>/result.md`

Where `<run-id>` is `TC-E-<NNN>-<HHMMSS>` (e.g. `TC-E-001-142300`).
Screenshots and artifacts go under `tests/e2e/results/<YYYY-MM-DD>/<run-id>/`.

---

## Result File Template

```markdown
# E2E Run Result — TC-E-<NNN>

**Run ID:** TC-E-<NNN>-<HHMMSS>
**Run timestamp:** YYYY-MM-DDTHH:MM:SSZ
**Test case:** tests/e2e/cases/<module>/TC-E-<NNN>-<slug>.md
**Environment:** <local | staging>
**Frontend URL:** <actual URL hit>
**Backend URL:** <actual URL hit>
**Browser:** chromium
**Auth as:** <user-key>
**Total duration:** Xs
**Verdict:** PASS | FAIL | BLOCKED

---

## 1. Step Results

| # | Step | Status | Duration | Screenshot |
|---|---|---|---|---|
| 1 | Login | PASS | 2.3s | screenshots/01-after-login.png |
| 2 | Navigate to Create Order | PASS | 0.8s | screenshots/02-create-order-form.png |
| 3 | Fill order form | FAIL | — | screenshots/03-fill-failed.png |

---

## 2. Verdict

### If PASS

```
All steps passed. No issues observed.
```

### If FAIL

**Failed step:** <#> — <step name>
**Error message:** <exact error from Playwright MCP>
**Last URL:** <URL when failure occurred>
**DOM snapshot:** dom-at-failure.txt (full accessibility tree at moment of failure)

**Console errors during run:**
```
<list of console.error messages from the browser>
```

**Network failures during run:**
```
<list of failed requests: METHOD URL → STATUS>
```

**Failure category:**
- [ ] **Bug in code** — UI behaviour deviates from the test case's expected outcome and the test case is correct
- [ ] **Stale test case** — A business rule, route, or selector legitimately changed; the case needs updating
- [ ] **Environment** — Seed data missing, service down, auth failed at the boundary
- [ ] **Flaky timing** — Element appeared after timeout; suggest retry or longer wait

**Reasoning:** <one paragraph explaining why this category was chosen, citing console/network evidence>

### If BLOCKED

**Blocked at:** Preconditions | Login | <other>
**Reason:** <e.g. "frontendUrl http://localhost:3000 not reachable", "test-users.json missing the 'admin' key">
**Resolution:** <what the human must do before this case can run>

---

## 3. Suggested Action (when FAIL)

### If Bug in code → Bug Ticket Draft

```markdown
**Title:** [<module>] <one-line description>
**Severity:** [High | Medium | Low]
**Reproduction:**
  1. /e2e TC-E-<NNN>
  2. Observe failure at Step <#>
**Expected:** <from the test case>
**Actual:** <observed>
**Last passing run:** <run-id or "unknown">
**Screenshots:** see tests/e2e/results/<date>/<run-id>/screenshots/
```

Recommend: `/planner` to create a bug ticket from this draft.

### If Stale test case → Refresh

Recommend: `/e2e-write TICKET-<ID>` to regenerate the case from the current ticket spec, then re-run.

### If Environment → Operator action

List exactly what needs to be fixed (seed data, service start, env var) and re-run.

### If Flaky → Retry

Re-run once. If it fails again with a different failure category, treat as that category. If it passes, mark in `tests/e2e/cases/_flaky.md` for follow-up.

---

## 4. Doc Sync (per `.agents/contracts/doc-sync.schema.md`)

E2E runs do NOT update documentation directly. However:
- A confirmed Bug → triggers a future `/dev` or `/fe` pass which produces its own Doc Sync Plan
- A confirmed Stale test → triggers `/e2e-write` which has its own ask-before-write step on the case file

The result file itself is the artifact — it is the doc, not a propagation. No Doc Sync Plan needed for the run.
```

---

## Verdict tags — strict semantics

| Tag | Meaning |
|---|---|
| **PASS** | Every step's Expected was observed within timeout. No console errors, no network failures. |
| **FAIL** | At least one step's Expected was not observed. Test case ran to the failing step. |
| **BLOCKED** | A precondition or environment issue prevented execution. The test never reached its first step. |

Do not invent additional tags. A flaky/timing failure is still **FAIL** with category "Flaky timing" — the test failed.

---

## Result file is append-only history

Never overwrite a previous result. Each run gets a fresh `<run-id>` directory. Diff between runs is meaningful — preserve it.
