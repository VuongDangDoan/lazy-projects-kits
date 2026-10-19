# Stack Pattern Library
> Pre-built pattern files for common tech stacks.
> Built once per stack → reused across all projects using that stack.
> `/onboard` copies the matching file into `knowledge/L0-global/[be|fe|mobile]-patterns.md`.

---

## How it works

```
/onboard asks: "Backend stack?"
     │
     ├── NestJS + TypeScript + PostgreSQL          → copy stacks/be/nestjs-ts-pg.md   → be-patterns.md
     ├── Next.js fullstack + TypeScript + PostgreSQL → copy stacks/be/nextjs-ts-pg.md → be-patterns.md
     ├── Django + Python + PostgreSQL              → copy stacks/be/django-python-pg.md → be-patterns.md
     ├── Not listed                                → use empty template → SA Agent fills from scratch
     └── ...

/onboard asks: "Frontend stack?"
     │
     ├── Next.js + shadcn/ui  → copy stacks/fe/nextjs-shadcn.md → fe-patterns.md
     │   NOTE: if Next.js fullstack was chosen for BE, set FE repo = same repo, FE = "none"
     │   and skip fe-patterns.md (BE patterns file already covers FE App Router patterns)
     ├── React + shadcn/ui + TanStack Query v5 → copy stacks/fe/react-shadcn-tanstack.md
     └── ...
```

---

## Next.js Fullstack — Single Repo Convention

When the project is a **Next.js fullstack monorepo** (API Routes + App Router in one repo):

- **BE repo** = the Next.js app repo (e.g. `my-app`)
- **FE repo** = `none` — frontend is part of the same repo
- `be-patterns.md` = copied from `stacks/be/nextjs-ts-pg.md` (covers Route Handlers, Prisma, Auth, Railway)
- `fe-patterns.md` = copied from `stacks/fe/nextjs-shadcn.md` (covers App Router, shadcn/ui, Client Components)
- Both pattern files are loaded — they cover different concerns of the same codebase
- `_source/[APP_REPO]/` is the single symlink — no `_source/[FE_REPO]/`

---

## Adding a new stack

1. Copy `stacks/_TEMPLATE.md` to `stacks/[be|fe|mobile]/[stack-slug].md`
2. Fill in all §§ sections with real patterns from a real project using that stack
3. The file grows over time as more projects use the same stack

---

## Stack files available

Only **4 stack files exist** today. Every other row below is a naming reservation only — the
file is absent from disk. `/onboard` must offer exactly the 4 existing files plus
"Other — patterns start from `knowledge/stacks/_TEMPLATE.md` and are filled by SA after the first codebase scan".

### Backend (`stacks/be/`)

| File | Stack | Status |
|------|-------|--------|
| `nestjs-ts-pg.md` | NestJS + TypeScript + PostgreSQL | ✅ complete |
| `nextjs-ts-pg.md` | Next.js fullstack + TypeScript + Prisma + PostgreSQL + Railway CI/CD | ✅ complete |
| `django-python-pg.md` | Django REST Framework + Python + PostgreSQL | ❌ NOT YET WRITTEN — use `_TEMPLATE.md` + SA scan |
| `laravel-php-mysql.md` | Laravel + PHP + MySQL | ❌ NOT YET WRITTEN — use `_TEMPLATE.md` + SA scan |
| `go-gin-pg.md` | Go + Gin + PostgreSQL | ❌ NOT YET WRITTEN — use `_TEMPLATE.md` + SA scan |
| `spring-kotlin-pg.md` | Spring Boot + Kotlin + PostgreSQL | ❌ NOT YET WRITTEN — use `_TEMPLATE.md` + SA scan |

### Frontend (`stacks/fe/`)

| File | Stack | Status |
|------|-------|--------|
| `nextjs-shadcn.md` | Next.js 14+ App Router + shadcn/ui + Tailwind CSS | ✅ complete |
| `react-antd-rqv3.md` | React 18 + Ant Design 5 + React Query v3 | ❌ NOT YET WRITTEN — use `_TEMPLATE.md` + SA scan |
| `react-shadcn-tanstack.md` | React 18 + shadcn/ui + TanStack Query v5 | ❌ NOT YET WRITTEN — use `_TEMPLATE.md` + SA scan |
| `vue3-element.md` | Vue 3 + Element Plus + Pinia | ❌ NOT YET WRITTEN — use `_TEMPLATE.md` + SA scan |
| `nuxt3.md` | Nuxt 3 + auto-imports | ❌ NOT YET WRITTEN — use `_TEMPLATE.md` + SA scan |

### Mobile (`stacks/mobile/`)

| File | Stack | Status |
|------|-------|--------|
| `react-native-expo.md` | React Native + Expo + React Navigation v6 | ✅ complete |
| `flutter.md` | Flutter + Dart + GoRouter | ❌ NOT YET WRITTEN — use `_TEMPLATE.md` + SA scan |
| `swift-uikit.md` | Swift 5 + UIKit (iOS) | ❌ NOT YET WRITTEN — use `_TEMPLATE.md` + SA scan |
| `kotlin-jetpack.md` | Kotlin + Jetpack Compose (Android) | ❌ NOT YET WRITTEN — use `_TEMPLATE.md` + SA scan |

---

## Stack file naming convention

`[framework]-[language]-[database].md` for BE
`[framework]-[ui-lib]-[data-layer].md` for FE
`[framework].md` for Mobile (platform is implicit)
