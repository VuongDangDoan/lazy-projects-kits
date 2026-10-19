# Test Case Schema v1.0
> QC Agent output MUST include every section below.
> Test cases must be executable — a developer reading them must know exactly what to test, what input to use, and what to expect.

---

## Required Output Files

### File 1: Test Cases — `tests/cases/[module]/TICKET-[ID]-tests.md`
### File 2: Security Notes — `tests/security/TICKET-[ID]-security.md`

**Security review is severity-scaled** (see §Security Notes Template below):
- **Full OWASP table** — required when ticket Layer includes BE, OR the ticket touches auth, permissions, or data handling
- **3-line N/A note** — allowed for everything else (pure UI tickets with no auth/permission/data-handling surface)

---

## Test Case File Template

```markdown
# Test Cases — TICKET-[ID]

**Module:** [module]
**US-ID:** US-NNN
**Ticket:** TICKET-[ID]
**QC Date:** YYYY-MM-DD
**Regression scope:** See `tests/regression-map.md` — section [module]

---

## 1. Unit Tests — Business Logic

### TC-[ID]-U01 — [Short test name]

**Type:** Unit
**Target:** `[ServiceName].[methodName]()`
**Business Rule:** BR-[ID]

**Setup:**
```
// Mock data / required state (language per stack)
```

**Input:**
```
// Specific input parameters
```

**Expected output:**
```
// Exact return value or side effect
```

**Assertions:**
- [ ] [Assertion 1]
- [ ] [Assertion 2]

---

### TC-[ID]-U02 — [Edge case]
...

---

## 2. Integration Tests — API

### TC-[ID]-I01 — [Endpoint + scenario]

**Type:** Integration
**Endpoint:** [METHOD] /[path]
**Scenario:** [Happy path | Error case | Edge case]

**Request:**
```json
{
  "field": "value"
}
```

**Expected Response — Status [code]:**
```json
{
  "field": "expected_value"
}
```

**Business Rule validated:** BR-[ID]
**AC validated:** AC[N] from US-NNN

---

## 3. State Transition Tests (if entity has a state machine)

### TC-[ID]-S01 — Valid transition

**From state:** [STATE_A]
**To state:** [STATE_B]
**Condition:** [...]
**Expected:** Transition succeeds, entity updated correctly

### TC-[ID]-S02 — Invalid transition (must throw)

**From state:** [TERMINAL_STATE]
**To state:** [any]
**Expected:** Throws the stack's validation/bad-request error with a message describing the invalid transition

---

## 4. Legacy Compatibility Tests (if dual-write is involved)

### TC-[ID]-L01 — Dual-write integrity

**Scenario:** Create a new record → verify legacy table also contains the record

**Steps:**
1. Call POST /[endpoint] with valid payload
2. Query the new table → verify record exists
3. Query the legacy table → verify record also exists
4. Compare data consistency between both tables

**Expected:** Both tables contain the record with no data conflicts

---

## 5. Regression Checklist

> Based on `tests/regression-map.md` — tests that must be re-run after this ticket.

- [ ] [Related module 1]: [specific test]
- [ ] [Related module 2]: [specific test]
```

---

## Security Notes Template

**Tier selection (per `roles/qc.md` Step 5):**
- Layer includes BE, OR ticket touches auth / permissions / data handling → use the **full template** below
- Otherwise → the security file may be just the **N/A note**:

```markdown
# Security Review — TICKET-[ID] — N/A
Layer: [FE | MOBILE] — no auth, permission, or data-handling surface in this ticket.
No security review required. Severity: None.
```

**Full template:**

```markdown
# Security Review — TICKET-[ID]

**Date:** YYYY-MM-DD
**Severity:** [None | Low | Medium | High | Critical]

---

## OWASP Check (applicable to this ticket)

| Risk | Applicable? | Status | Note |
|---|---|---|---|
| Injection (SQL/NoSQL) | [Yes/No] | [Pass/Fail/NA] | [Note] |
| Broken Authentication | [Yes/No] | [Pass/Fail/NA] | [Note] |
| Sensitive Data Exposure | [Yes/No] | [Pass/Fail/NA] | [Note] |
| Broken Access Control | [Yes/No] | [Pass/Fail/NA] | [Note] |
| Mass Assignment | [Yes/No] | [Pass/Fail/NA] | [Note] |

---

## Input Validation Check

- [ ] Input DTO/schema is validated per the stack's validation pattern (be-patterns.md §Validation)
- [ ] Integer fields have range constraints (min/max)
- [ ] String fields have maxLength constraints
- [ ] Enum fields reject values outside the defined list

---

## Issues Found

### [SEVERITY] — [Issue description]
**Location:** [file + line]
**Risk:** [Description of the risk]
**Fix:** [Specific remediation recommendation]

---

## Verdict

[ ] **Approved** — No issues found
[ ] **Approved with notes** — Minor issues present, does not block merge
[ ] **Blocked** — Issues must be resolved before merge
```

---

## Validation Checklist — QC Agent self-checks before handoff

- [ ] At least 1 unit test per business rule referenced in the ticket
- [ ] At least 1 happy path test AND 1 error case test
- [ ] Integration tests cover all ACs from the US
- [ ] If state machine exists → valid and invalid transition tests included
- [ ] If dual-write exists → legacy compatibility test included
- [ ] Security review completed at the correct tier (full table for BE/auth/permissions/data-handling; N/A note otherwise)
- [ ] Regression checklist verified against `regression-map.md`
- [ ] Every test case has a concrete expected output — "should work" is not acceptable
