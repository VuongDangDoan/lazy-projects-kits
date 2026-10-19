# Legacy Scan Schema v1.0
> Must be completed before any Build task that touches legacy code.
> Claude asks each section one by one. Human answers. Claude fills in the scan file.
> No completed scan = Build agent is blocked.
> The scan covers **whichever repo(s) the module touches** — BE, FE, and/or mobile. Scan the `_source/` repo(s) relevant to the ticket, not only the backend.

---

## Template

```markdown
# Legacy Scan — [Module] / [TICKET-ID]

**Module:** [module]
**Ticket:** TICKET-[ID]
**Scan date:** YYYY-MM-DD
**Breaking risk:** [High | Medium | Low]

---

## 1. Legacy Endpoints Involved

| Legacy Endpoint | Method | Current Callers | Action | Notes |
|---|---|---|---|---|
| /api/v0/[path] | POST | Frontend module X | Dual-write | Preserve response format |
| /api/v0/[path] | GET | Mobile app | Deprecate after Sprint 3 | Redirect to v1 |

**Action options:** Keep | Dual-write | Deprecate | Redirect | Remove *(Remove requires an ADR)*

---

## 2. Legacy Database Tables Involved

| Table | Columns in use | Columns safe to ignore | Migration plan |
|---|---|---|---|
| [table_name] | col1, col2, col3 | old_status | Add new columns only, nothing removed |
| [table_name] | col1 | — | No changes |

**Absolute constraints:**
- NEVER DROP a legacy table
- NEVER DROP a legacy column
- NEVER RENAME anything in a legacy table
- NEVER change the data type of a legacy column

---

## 3. Legacy Business Logic to Preserve

> Behavior currently running in legacy code that has no spec or document.
> Human must answer this section — Claude must not infer or assume.

**Current validation rules:**
- [Describe what is being validated in the legacy code]

**Calculation logic:**
- [Formula or condition currently being computed]

**Error format the frontend currently expects:**
```json
{
  "error": "...",
  "code": "..."
}
```

**Current side effects (email, notification, log, external call):**
- [List specifically]

---

## 4. Reverse Dependencies

> Other services, modules, or frontends that currently depend on this legacy code.

| Dependent | Depends on | Impact if changed |
|---|---|---|
| Frontend module A | Response format of GET /v0/[path] | UI breaks if field name changes |
| Background job X | Table [name] column [col] | Job fails if column is removed |

---

## 5. Current Test Coverage

- Tests exist: [Yes / No]
- Test file location: [path or N/A]
- Estimated coverage: [% or N/A]
- Behavior covered by tests: [Description or N/A]

**If no tests exist:** Dev Agent must write a smoke test for the legacy path before modifying it.

---

## 6. Risk Assessment

**Breaking risk:** [High | Medium | Low]

**Reason:**
- [Reason 1]
- [Reason 2]

**Rollback plan:**
- [Specific description — must not be left blank]

**Feature flag required:**
- [ ] Yes — because [reason]
- [ ] No

---

## 7. Action Plan for Dev Agent

> Concrete summary of what Dev must do with legacy. Read this and start immediately.

- [ ] Dual-write to [table] using format: [description]
- [ ] Preserve response format of [endpoint]
- [ ] Write smoke test for [legacy path] before modifying
- [ ] Update [legacy field] according to logic: [description]
- [ ] DO NOT touch: [list of files / tables / columns]
```

---

## Validation Checklist

- [ ] All 7 sections completed — no section left blank
- [ ] "None" must be written explicitly — blank is not acceptable
- [ ] Rollback plan is specific (not "revert the commit")
- [ ] Section 7 action plan is actionable — Dev reads it and knows exactly what to do
- [ ] File saved to the correct path: `knowledge/L2-legacy/scans/[module]-legacy-scan.md`

---

## Re-scan protocol (STALE or source drift)

When a scan goes stale (>30 days, SHA mismatch, or a discrepancy is found between §7 and the actual source):

1. Move the old scan wholesale to `knowledge/L2-legacy/scans/[module]-legacy-scan-archive.md` (append below any prior archived scans, with a `## Archived YYYY-MM-DD` divider)
2. Run `/legacy-scan [module]` fresh — **replace** the scan file wholesale; do not append rounds to the live file
3. The live file always contains exactly one current scan — history lives only in the archive

This replaces any older "never overwrite, only append" guidance: the live scan is replaced; the archive preserves history.
