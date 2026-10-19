# E2E Test Case Schema v1.0
> Format for E2E test cases executed by the E2E Tester Agent via Playwright MCP.
> Distinct from `tests/cases/` (unit + integration) — those test code, these test the running system.

---

## File Location

`tests/e2e/cases/<module>/TC-E-<NNN>-<short-slug>.md`

Example: `tests/e2e/cases/order/TC-E-001-create-order-happy-path.md`

ID convention: `TC-E-NNN` zero-padded — **global sequence** via `scripts/next-id.sh e2e`, never hand-counted. IDs are stable — once assigned, never reuse.

---

## Required Output File Template

```markdown
# E2E Test Case — TC-E-<NNN> — <Short Title>

**Module:** [module slug from project.config.json]
**Linked ticket:** TICKET-<ID> (or "—" if standalone regression)
**Linked AC:** AC<N> from US-<XXX> (or "—")
**Created:** YYYY-MM-DD
**Owner:** E2E Agent
**Browser:** chromium
**Auth as:** <user-key from test-users.json> (e.g. admin, order_manager)
**Environment:** local (default — override at runtime: `/e2e TC-E-XXX --env=staging`)
**Tags:** [smoke | regression | happy-path | error-path | ...]

---

## 1. Preconditions

> What must be true in the environment before this case can run.
> The agent verifies these and aborts with BLOCKED if any fails.

- [ ] Backend reachable at the env's `backendUrl`
- [ ] Frontend reachable at the env's `frontendUrl`
- [ ] Test user `<user-key>` can log in
- [ ] Seed data: <list any specific records the test needs, e.g. "Customer 'Acme Corp' exists">
- [ ] Feature flag: <e.g. external-sync flag disabled during test — or "None">

---

## 2. Steps

> Numbered, atomic. Each step has a single Action and a single Expected outcome.
> The agent executes steps in order. On failure, it stops and writes a failure report — does not continue.

### Step 1 — <Short action name>

**Action:**
- <Concrete UI action: navigate to URL, click element, fill field, etc.>
- Use natural language; the agent translates to Playwright MCP calls (browser_navigate, browser_click, browser_type, etc.)

**Expected:**
- <Observable result: URL changes to X, notification "Y" appears, element with text "Z" visible>

**Screenshot:** `01-<short-slug>.png` (saved under results/<run-id>/screenshots/)

---

### Step 2 — <Next action>

**Action:** <...>
**Expected:** <...>
**Screenshot:** `02-<short-slug>.png`

---

<Repeat for each step. Keep total steps ≤ 15 per case — split larger flows into multiple cases.>

---

## 3. Cleanup

> What the agent should do after the run, regardless of pass/fail.
> Pick ONE strategy per case:

- **API cleanup:** call DELETE /v1/<resource>/<id> for any record created
- **UI cleanup:** navigate back and delete via UI
- **Skip:** rely on test DB reset between runs (note this here)
- **N/A:** read-only test, nothing to clean

---

## 4. Failure analysis hints

> Optional but recommended. Helps the agent classify failures correctly.

- If Step <N> fails with "<error pattern>" → likely <Bug | Stale test | Environment | Flaky>
- If <element> not found within timeout → check <hypothesis>

Example:
- If Step 3 fails with "Customer not found" in dropdown → likely Environment (seed data missing), not a code bug
- If Step 3 fails with HTTP 422 validation error → likely Stale test (a BR changed); re-run /e2e-write to refresh
```

---

## Self-check before handoff (E2E Agent)

- [ ] ID follows `TC-E-NNN` format (global, via `scripts/next-id.sh e2e`) and is unique under `tests/e2e/cases/`
- [ ] Module is a slug from `project.config.json` modules[]
- [ ] Browser, auth, and environment fields filled
- [ ] At least 1 precondition listed (even "user can log in")
- [ ] Each step has BOTH Action AND Expected — no step has just one
- [ ] Total steps ≤ 15
- [ ] Cleanup strategy chosen
- [ ] Screenshots numbered sequentially with descriptive slugs

---

> Why markdown and not `.spec.ts`? See `tests/e2e/README.md` §"Why markdown".
