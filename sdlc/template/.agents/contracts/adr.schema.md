# Architecture Decision Record (ADR) Schema
> SA Agent produces an ADR when a non-obvious trade-off, new pattern, or new dependency is introduced.
> File location: `architecture/decisions/[NNN]-[kebab-title].md`
> Get the next ADR number via `scripts/next-id.sh adr` — do not hand-count.

---

## When to produce an ADR (mandatory vs skip)

**Mandatory — always produce when:**
- A new external dependency (package, service, SDK) is introduced
- A new architectural pattern is adopted that differs from existing patterns in the codebase
- A breaking change is made to an API, event payload, or database schema that callers depend on
- A legacy behavior is intentionally changed or removed (dual-write, column rename, endpoint removal)
- Two or more valid approaches were considered and one was chosen — the rejected alternatives must be recorded

**Skip — note "ADR skipped: conventional" when:**
- The change follows an existing pattern already documented in `be-patterns.md`, `fe-patterns.md`, or `mobile-patterns.md`
- A new field is added to an existing endpoint (additive, no callers affected)
- Pure refactor with no architectural impact

When skipping, add this one-liner to the api-contract yaml `x-dev-notes.new_dependencies` field:
```
ADR: skipped — conventional [reason]
```

---

## ADR File Template

```markdown
# ADR-[NNN] — [Title: short decision statement]
> Status: [Proposed | Accepted | Deprecated | Superseded by ADR-NNN]
> Date: [YYYY-MM-DD]
> Deciders: [SA Agent + human reviewer]
> Ticket context: [TICKET-ID or US-ID]

---

## Context

[2–4 sentences: what situation forced this decision?
Include: the constraint, the business requirement, or the technical gap that made this necessary.
Do NOT describe the solution here — only the problem space.]

## Decision

[1–3 sentences: what was decided, stated as a firm commitment.
Use active voice: "We will use X" / "We adopt pattern Y" / "We introduce dependency Z".]

## Consequences

### Positive
- [What gets better as a result of this decision]
- [Performance gain, maintainability, consistency, reduced duplication, etc.]

### Negative / Trade-offs
- [What gets harder or more complex]
- [New maintenance burden, learning curve, future migration cost, etc.]

### Risks
- [Known unknowns — things that could go wrong and must be monitored]

## Alternatives Considered

| Option | Why rejected |
|---|---|
| [Alternative A] | [specific reason — not "it was worse"] |
| [Alternative B] | [specific reason] |

## Migration / Rollback Plan

[If this decision is reversible: describe the rollback steps.]
[If this decision is irreversible (e.g. DB schema drop): state that explicitly and describe the mitigation.]

## References

- [Link to ticket, US, or domain file that motivated this decision]
- [Link to external documentation, RFC, or pattern this follows]
```

---

## Validation Checklist — SA self-checks before handoff

- [ ] Status is set (Proposed until human approves, then Accepted)
- [ ] Context explains the PROBLEM, not the solution
- [ ] Decision is stated as a firm commitment (active voice)
- [ ] At least one alternative listed with a specific rejection reason
- [ ] Consequences has both positive AND negative entries (no decision is cost-free)
- [ ] Migration / rollback plan present — or explicitly marked "irreversible"
- [ ] File named `[NNN]-[kebab-title].md` with correct sequential number
- [ ] ADR number added to api-contract yaml `x-dev-notes` or US handoff notes

---

## Breaking Change ADR — additional required fields

When the ADR documents a breaking change (API, event, DB schema), append this block:

```markdown
## Breaking Change Detail

**What breaks:** [exact field/endpoint/event/table that changes]
**Who is affected:** [FE / Mobile / External callers / Other services]
**Deprecation timeline:** [N sprints / date — how long old behavior stays live]
**Migration path for callers:**
  1. [Step callers must take]
  2. [Step callers must take]
**Backward-compat ticket:** [TICKET-ID — the ticket that keeps old behavior live during transition]
```
