---
description: Configure CI/CD + deployment — copies parameterized configs from templates/devops/ into the app repo; secrets are set by the human in dashboards/CLI, never pasted into chat.
argument-hint: (no arguments — interactive; re-run any time to change platform)
---

# /devops — CI/CD & Deployment Setup

Run after `/onboard` and repo symlinks. Re-runnable. $ARGUMENTS is ignored — interactive.

**Security rule (absolute):** NEVER ask the user to paste secrets into this chat — no tokens,
SSH keys, service-account JSON, or DB passwords. Secrets are set by the human in the platform
dashboard or via CLI in their own terminal (`gh secret set NAME` reads from stdin). This command
only tells them WHICH secrets to set and WHERE.

---

## Pre-flight

- Read `project.config.json`. If missing or `initialized: false` → "Run `/onboard` first."
- Read `knowledge/L0-global/git-workflow.md` — it defines the branch strategy (main/develop/…).
  Use it as the default; confirm rather than re-ask.
- Check the BE repo symlink: `ls _source/[repos.be.name]` — if missing → "Set up symlinks
  (/onboard Phase 8) first, then re-run /devops."

---

## Phase 1 — Interview (one message)

```
Setting up CI/CD for [project.name].

1. CI + platform — pick a shipped option:
   A) GitHub Actions + Railway     (templates/devops/github-actions-railway/)
   B) GitLab CI + Railway          (templates/devops/gitlab-ci-railway/)
   C) GitHub Actions + Vercel      (templates/devops/vercel/)
   D) GitHub Actions + Docker VPS  (templates/devops/vps-docker/)
   E) Other (Fly.io, AWS ECS, GCP Cloud Run, …) — supported manually: I can draft
      configs from your platform's docs on request; no shipped template.

2. Environments:  A) Production only   B) Production + Staging   C) Production + PR previews

3. Branch strategy — git-workflow.md says prod=[main], staging=[develop]. Confirm or override.
```

---

## Phase 2 — Generate Configs from templates/devops/

Copy the chosen option's files from `templates/devops/<option>/` into `_source/[repos.be.name]/`
(GitHub workflow files go under `.github/workflows/`), substituting the `{{PLACEHOLDERS}}`
listed in `templates/devops/README.md`.

Substitution values — stack-conditional from `project.config.json` (`repos.be.stack`), never hard-coded:

| repos.be.stack contains | INSTALL_CMD | SETUP_CMD | CHECK_CMD | LINT_CMD | BUILD_CMD | MIGRATE_CMD | START_CMD |
|---|---|---|---|---|---|---|---|
| Next.js (Prisma) | `npm ci` | `npx prisma generate` | repos.be.check_cmd | `npm run lint` | `npm run build` | `npx prisma migrate deploy` | `npm start` |
| NestJS (TypeORM) | `npm ci` | `true` | repos.be.check_cmd | `npm run lint` | `npm run build` | `npm run migration:run` (confirm script name) | `npm run start:prod` |
| Django | `pip install -r requirements.txt` | `true` | repos.be.check_cmd | `ruff check .` (confirm) | `true` | `python manage.py migrate` | `gunicorn app.wsgi` |
| Laravel | `composer install` | `true` | repos.be.check_cmd | `./vendor/bin/pint --test` (confirm) | `true` | `php artisan migrate --force` | `php artisan serve` |
| Go | `go mod download` | `true` | repos.be.check_cmd | `true` | `go build ./...` | confirm migration tool | confirm binary |
| Other | ask the user (show the commands you inferred; confirm) | | | | | | |

Also substitute: `{{BE_REPO}}` = repos.be.name · `{{NODE_VERSION}}` = 20 (confirm) ·
`{{PROD_BRANCH}}` / `{{STAGING_BRANCH}}` from Phase 1 Q3 · `{{HEALTHCHECK_PATH}}` = `/api/health`
(or an existing route — see Phase 4) · `{{GH_ORG}}` (vps-docker compose image path).

Rules:
- Skip `deploy-staging.yml` if Production-only.
- **Quality gate is opt-OUT:** every template's deploy job has `needs: [check]` — keep it.
  Only remove if the user explicitly asks, and note the risk.
- **Idempotent re-run:** before writing, check if the destination file exists. If it exists and
  differs, show the diff and ask per file before overwriting — never blanket-overwrite.
- After writing, check for unreplaced template markers: `grep -En '\{\{[A-Z_]+\}\}' <written files>`
  — must be empty. (GitHub Actions' own `${{ secrets.X }}` syntax is lowercase-dotted and won't match.)

---

## Phase 3 — Secrets Checklist (human sets them — never in chat)

Output the checklist for the chosen option. The user runs CLI commands in THEIR terminal.

**GitHub Actions secrets** — set via repo Settings → Secrets and variables → Actions, or:
`gh secret set NAME` (then type/paste the value into the terminal prompt — not into this chat).

| Option | Secrets to set | Where the value comes from |
|---|---|---|
| Railway | `RAILWAY_TOKEN` | Railway → Account Settings → Tokens |
| | `RAILWAY_SERVICE_ID_PROD` (+`_STAGING`) | Railway service → Settings → Service ID |
| Vercel | `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID` | Vercel account/project settings |
| VPS | `VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY`, `DEPLOY_PATH` | user generates a dedicated CI deploy key in their terminal (`ssh-keygen -t ed25519 -f ~/.ssh/deploy_key`), adds the pub key to the VPS, sets the private key via `gh secret set VPS_SSH_KEY < ~/.ssh/deploy_key` |
| GitLab | same Railway vars | GitLab project → Settings → CI/CD → Variables (masked) |

**App runtime env (platform dashboard, NOT CI secrets):** `DATABASE_URL` (Railway injects it
when you add a PostgreSQL service), `NEXTAUTH_SECRET` (user runs `openssl rand -base64 32`
locally), `NEXTAUTH_URL`, `NODE_ENV=production`. For VPS: these live in `[DEPLOY_PATH]/.env`
on the server, created by the user over SSH.

Platform one-time setup (Railway example): create project → add PostgreSQL service → connect
repo to app service (branch = prod branch) → set env vars above → optional custom domain.

---

## Phase 4 — Healthcheck + Summary

**Healthcheck endpoint must exist.** `railway.toml` (and any platform healthcheck) points at
`{{HEALTHCHECK_PATH}}`. Verify the route exists in `_source/[repos.be.name]/` — if not, either
create a minimal `/api/health` route (200 + `{status:"ok"}`) as part of this pass, or point
`healthcheckPath` at an existing route. **Verify before the first deploy** — a missing
healthcheck makes every deploy fail as unhealthy.

```
## /devops Complete — [project.name]
CI/CD: [option]        Environments: [answer]        Branches: [prod]/[staging]
Files written to _source/[repos.be.name]/:   [list]
Secrets still to set (by YOU, in dashboard/terminal):   [list from Phase 3]
Healthcheck: [route exists | created /api/health | ACTION NEEDED]
Next: complete the secrets checklist → push a test commit → watch the pipeline
      (check job must pass BEFORE deploy runs) → verify healthcheck returns 200.
```

---

## Error Handling

- **Option E (no shipped template):** draft configs from the platform's docs with the user,
  following the same rules (check gates deploy; secrets never in chat; healthcheck verified).
- **Stack not in the Phase 2 table:** show inferred commands, get confirmation before writing.
- **Existing configs differ on re-run:** diff + per-file confirmation (Phase 2 rule).
