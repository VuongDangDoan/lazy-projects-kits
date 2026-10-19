# Security

This file documents what flows out of this workspace, who sees it, and what's the user's responsibility. **Read before connecting any AI provider or MCP server.**

---

## What this workspace contains

Sensitive in aggregate, even though no individual file is "secret":

| Content | Path | Why it's sensitive |
|---|---|---|
| Full attack-surface map | `architecture/feature-map/` | Every endpoint URL, FE route, and permission gate. Reconnaissance gold. |
| Legacy DB schema + business logic | `knowledge/L2-legacy/scans/<module>-legacy-scan.md` | Table names, columns, business rules, reverse dependencies, integration points |
| Internal data model | `knowledge/L1-domain/<module>-domain.md` | Entities, relationships, calculations, state machines |
| Architectural decisions | `architecture/decisions/*.md` | How and why we build, what's deferred |
| Vendor integration details | Any dual-write / external-system sync references | Where the system integrates with vendor systems |
| In-flight planning | `docs/brd.md`, `docs/srs/`, `knowledge/L3-session/active-context.md` | Current sprint state, deferred features, business rationale |
| Local environment paths | `_source/` symlinks resolve to local repo paths | Local file structure |

This doesn't include secrets per se (no API keys, no PII, no customer data) — but in aggregate it is a complete **internal architecture description of your system**. If it leaked publicly, it would describe your feature set, attack surface, integration points, and roadmap.

---

## Who sees it (data flows)

Every time you run an AI agent against this workspace, the agent reads files into a prompt and sends it to a third-party API.

| Provider | When it sees content | Provider data policy (verify with current ToS) |
|---|---|---|
| **Anthropic** (Claude Code, Claude API) | Every `/ba`, `/sa`, `/dev`, `/fe`, `/qc`, `/review`, `/legacy-scan`, etc. invocation in Claude Code | Commercial API: not used for training; logs retained ~30 days for abuse monitoring. See [anthropic.com/privacy](https://www.anthropic.com/privacy). |
| **OpenAI** (Codex CLI, ChatGPT) | Every Codex invocation that has access to the workspace | Varies by product/tier. See [openai.com/policies](https://openai.com/policies). |
| **Google** (claude_ai_Google_Drive MCP, if connected) | Any Google Drive query the agent runs | Google Workspace data policy applies. Don't connect this MCP for sensitive workspaces. |
| **Local** (Playwright MCP, computer-use MCP) | Run on your machine; data does not leave | Browser test runs and screenshots stay local. Computer-use captures screen content only when invoked. |
| **Git remote** (`origin`) | Anything you `git push` | Per your organization's git-hosting policy (GitHub/GitLab, cloud or self-hosted). |

**Claude Code memory files** (`~/.claude*/**/memory/`) persist across sessions and are loaded into context every session — review what's saved there periodically.

---

## What's gitignored (won't be pushed to remote)

See [.gitignore](.gitignore) for the full list. Key entries:

- `_source/` — symlinks to source repos (don't follow into the workspace history)
- `knowledge/L3-session/active-context.md` and `history/` — local session state
- `tests/e2e/fixtures/test-users.json`, `auth-state.json` — real test creds
- `.env`, `.env.*` (except `.env.example`)
- Private keys: `*.pem`, `*.key`, `id_rsa*`, `id_ed25519*`
- Cloud credentials: `credentials*.json`, `service-account*.json`, `gcp-key*.json`, `aws-credentials*`
- Test results: `tests/results/`, `tests/e2e/results/`
- OS / editor noise: `.DS_Store`, `.idea/`, `*.swp`, etc.

---

## Automated guards

| Guard | What it does | Where |
|---|---|---|
| **Pre-commit secret scanner** | Blocks commits containing AWS keys, GitHub/GitLab/OpenAI/Anthropic/Slack tokens, private keys, JWTs, DB connection strings with passwords, generic password assignments. Runs in this workspace by default; with `--include-source`, also runs in source repos (see "The 3-repo gap" below). | `scripts/check-secrets.sh` (auto-runs from `scripts/git-hooks/pre-commit` and from source-repo wrappers) |
| **Pre-commit validators** | Block malformed tickets / user stories / feature-maps / domain files / legacy scans / API contracts / test cases / e2e cases | `scripts/validate-*.py` |
| **Audit aggregator** | Runs every check on demand or on a schedule (`scripts/audit.sh` — 14 sections) | `scripts/audit.sh` |
| **Doc Sync protocol** | Every code-touching agent must produce a doc-update plan; non-trivial changes wait for human approval at G4 (trivial propagation uses the auto-approve tier). Prevents agents silently propagating sensitive content into docs. | `.agents/contracts/doc-sync.schema.md` |

To activate the pre-commit hook in a fresh clone:
```bash
scripts/install-hooks.sh                  # this workspace only
scripts/install-hooks.sh --include-source # also installs in every repo from project.config.json
                                          # (prints a husky setup hint for repos using core.hooksPath)
```

To run the secret scanner manually on the whole repo:
```bash
scripts/check-secrets.sh --all
```

### The 3-repo gap (important)

When agents (`/dev`, `/fe`, `/mobile`) write code, the file lands in a source repo — a **separate git repo** from this workspace. **The workspace's pre-commit hook does NOT run on commits made there.** Each source repo has its own `.git/hooks/`.

This workspace ships a thin wrapper hook (`scripts/git-hooks/source-repo-pre-commit`) that defers to the workspace's `check-secrets.sh`. Install it via:

```bash
scripts/install-hooks.sh --include-source
```

| Source repo situation | What `--include-source` does |
|---|---|
| Plain `.git/hooks/` | Installs the wrapper hook automatically (safe to install) |
| `core.hooksPath` set (husky etc.) | **Cannot auto-install** — `.git/hooks/pre-commit` would be ignored. The installer prints the exact one-line call to add to the repo's tracked hook file (needs a code-review commit in that repo). |

Without `--include-source`, agents writing source code have **no automated secret-scan defense at commit time**. Run `scripts/install-hooks.sh --include-source` once per fresh clone of any repo.

The wrapper auto-locates the workspace by searching sibling directories for `scripts/check-secrets.sh`. Override with the `SDLC_WORKSPACE=/path/to/workspace` env var if your layout differs.

---

## User responsibility

Things automated guards can't catch — **only the user can**:

1. **Don't paste real customer data** (PII, real names, ID numbers, payment details, phone numbers) into ticket descriptions, user stories, or agent prompts. Use synthetic placeholders.
2. **Don't include real production database dumps or rows** in legacy scans. The scan describes shape; real values stay in the database.
3. **Don't paste API keys, passwords, or tokens** into chat — even ephemerally. They get logged.
4. **Review Claude Code memory files** (`~/.claude*/**/memory/`) periodically. Remove anything sensitive that accumulated unintentionally.
5. **Don't connect cloud MCP servers** (Google Drive, etc.) for this workspace unless your org has done a vendor risk review. Local MCPs (Playwright, computer-use) are fine.
6. **Don't ask agents to fetch URLs** that contain sensitive query parameters (auth tokens in URL, customer IDs, etc.).
7. **Sanitize agent output before posting externally** (PRs, Slack, GitHub issues). Internal terms, `_source/` absolute paths, real customer IDs, and verbatim DB column names should be replaced or removed.
8. **For sensitive features** (financial, legal, compliance-blocking), consider running the work entirely in a source repo without involving this workspace's AI agents.

---

## Reporting a leak

If you suspect a secret or sensitive data was exposed:

1. **Rotate the credential immediately** (don't wait for analysis).
2. **Check git history**: `git log --all -p | grep -i <pattern>`
3. **If the leak was pushed**: notify your security team; treat the credential as compromised regardless of how short the exposure was.
4. **Add the pattern to `scripts/check-secrets.sh`** so it doesn't recur.
5. **Document the incident** for follow-up.

Public push = public secret. Rotation is mandatory.

---

## Vendor data-policy review checklist (for compliance)

Before introducing a new AI provider, MCP server, or external integration:

- [ ] Is the vendor's data-retention policy documented?
- [ ] Does the vendor commit to not training on inputs? (Check current ToS, not yesterday's.)
- [ ] Where does the data physically reside? (Region matters for some compliance regimes.)
- [ ] Does your organization have a Data Processing Agreement (DPA) with the vendor?
- [ ] Has the security team approved the vendor for this workspace's sensitivity tier?

---

## Threat model summary

This workspace is internal-only. The realistic threats are:

1. **Accidental commit + push** of a real credential → caught by `check-secrets.sh` (pre-commit)
2. **Provider data breach** (Anthropic / OpenAI / Google) → out of our control; relies on provider security posture
3. **Memory file accumulation** of sensitive details → user discipline + periodic review
4. **External output contamination** (PR descriptions, Slack messages) → user discipline + sanitization
5. **MCP server data flow** (cloud MCPs) → don't connect cloud MCPs for sensitive sessions

What this workspace does NOT defend against (out of scope):
- Local machine compromise (an attacker with root on your laptop sees everything)
- Internal threat actors with repo access
- Vulnerabilities in `_source/` source code itself (separate concern; see the source repos' own security docs)
