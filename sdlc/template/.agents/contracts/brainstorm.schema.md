# Brainstorm Output Contract v1.0
> Brainstorm Agent output. Goes into `knowledge/L3-session/active-context.md` — there is no per-feature artifact file.
> Any missing field = incomplete output. BA cannot proceed without an Agreed approach.

---

## Where it lands

Two places, written in the same pass:

1. **`knowledge/L3-session/active-context.md` — Feature Brief section** (persistent state for the next agent)
2. **Handoff block in the chat reply** (visible signal to the human + next-agent prompt)

The chat handoff is a copy of the Feature Brief plus the next command.

---

## Feature Brief — required fields

```markdown
## Feature Brief

**Topic:** [one-line description of what was brainstormed]
**Module:** [module slug from project.config.json]
**Agreed approach:** Solution [N] — [Short name]

**Why this approach:**
- [1–3 bullets on why this beat the alternatives — keep specific, not generic]

**Key decisions locked:**
- [Decision 1 — anything BA / SA / Dev MUST honor]
- [Decision 2 — ...]

**Constraints to carry forward:**
- [What BA / SA / Dev must NOT change or assume — e.g. "do not introduce a new module", "must reuse the existing base-service pattern (be-patterns.md §3)"]

**Open questions / caveats:**
- [Anything still undecided that BA must clarify before writing the story — or "None"]

**Legacy impact:** [None | Low | High] — [one line: which tables/endpoints]
**Effort estimate:** [XXS | XS | S | M | L | XL]
```

---

## Handoff block — required format

Output this in the chat reply after the human approves the recommendation:

```
## Brainstorm Complete ✓

Agreed solution: Solution [N] — [Name]

Key decisions locked:
- [Decision 1]
- [Decision 2]

Constraints to carry forward:
- [Anything BA/SA/Dev must NOT change or assume]

active-context.md updated: Feature Brief section ✓

Next step:
  /ba [refined feature description based on agreed solution]
```

---

## Validation Checklist — Brainstorm Agent self-checks before handoff

- [ ] Topic, Module, and Agreed approach all filled
- [ ] At least 1 entry under "Why this approach"
- [ ] At least 1 entry under "Key decisions locked"
- [ ] "Constraints to carry forward" filled (even if "None — proceed with default conventions")
- [ ] "Open questions" filled — write "None" explicitly if there are no open questions
- [ ] Legacy impact
- [ ] Effort estimate assigned
- [ ] Human has explicitly approved the recommendation before this brief is written
- [ ] Handoff block points at the next command (`/ba` for new feature; could be `/sa` if BA work is already done)
