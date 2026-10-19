# DevOps Template Library
> Config files copied by `/devops` into `_source/{{BE_REPO}}/`, substituting `{{PLACEHOLDER}}` markers.
> Only the 4 option directories below are shipped. Other CI/platform combinations are
> supported manually: the agent can draft configs from your platform's docs on request.

## Shipped options

| Directory | CI provider | Platform | Files |
|---|---|---|---|
| `github-actions-railway/` | GitHub Actions | Railway | `ci.yml`, `deploy-prod.yml`, `deploy-staging.yml`, `railway.toml` |
| `gitlab-ci-railway/` | GitLab CI | Railway | `.gitlab-ci.yml` |
| `vercel/` | GitHub Actions | Vercel | `ci.yml`, `deploy.yml` |
| `vps-docker/` | GitHub Actions | Docker + VPS | `Dockerfile`, `docker-compose.yml`, `deploy.yml` |

## Placeholders

Substituted by `/devops` from `project.config.json` + its stack table:

- `{{BE_REPO}}` — repo name (repos.be.name)
- `{{NODE_VERSION}}` — runtime version (default `20`)
- `{{INSTALL_CMD}}` — e.g. `npm ci`
- `{{SETUP_CMD}}` — pre-build codegen, e.g. `npx prisma generate` (Prisma stacks) or `true` (none)
- `{{CHECK_CMD}}` — typecheck, from `repos.be.check_cmd` in project.config.json
- `{{LINT_CMD}}` — e.g. `npm run lint`
- `{{BUILD_CMD}}` — e.g. `npm run build`
- `{{MIGRATE_CMD}}` — e.g. `npx prisma migrate deploy` or `true` (none)
- `{{START_CMD}}` — e.g. `npm start`
- `{{HEALTHCHECK_PATH}}` — e.g. `/api/health` — the route MUST exist before first deploy
- `{{PROD_BRANCH}}` / `{{STAGING_BRANCH}}` — from `knowledge/L0-global/git-workflow.md` (default `main` / `develop`)

## Design rule — quality gate is opt-OUT

Every deploy job `needs: [check]` (typecheck + lint run BEFORE deploy). Removing that
dependency is a deliberate opt-out the human makes by editing the generated file — the
templates never ship with the gate disabled.
