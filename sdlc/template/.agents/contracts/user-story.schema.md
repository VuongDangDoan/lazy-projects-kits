# User Story Contract v2.0
> BA Agent output. Token-trimmed: removed Epic/Priority/Status (tracked elsewhere),
> Complexity (SA owns it via `x-dev-notes`), and verbose Legacy Notes (replaced with boolean + ref).

---

## Template

```markdown
## [US-ID] — [Short Title, ≤10 words]

**Module:** [module slug from project.config.json]

---

### User Story
As a **[role]**, I want to **[specific action]** so that **[measurable benefit]**.

---

### Business Rule Refs
- BR-[ID]: [name]      # only rules that apply; "None" if truly none

---

### Acceptance Criteria
> GIVEN–WHEN–THEN. 2-6 ACs. At least 1 happy path + 1 error case.

**AC1 — Happy path:**
GIVEN [...] WHEN [...] THEN [...]

**AC2 — Error / edge:**
GIVEN [...] WHEN [...] THEN [...]

---

### SA Handoff Notes
**Entities involved:**
- [Entity]: create | read | update | delete | state-change

**Business logic SA must know:**
- [Conditions, validations, calculations]

**Inter-module events:**
- After [action] → emits [event] to [module]    # omit line if none
- Receives [event] from [module]                # omit line if none

---

### Legacy
**Touches legacy?** [No | Yes — see `knowledge/L2-legacy/scans/[module]-legacy-scan.md`]
```

---

## Validation Checklist — BA self-checks before handoff

- [ ] ID format `US-NNN` — global sequence, obtained via `scripts/next-id.sh us` (never hand-counted)
- [ ] Module is a slug from `project.config.json` modules[]
- [ ] User story has role + action + benefit
- [ ] At least 1 happy path AC + 1 error AC, all in GIVEN–WHEN–THEN
- [ ] SA Handoff Notes complete enough that SA needs zero follow-up
