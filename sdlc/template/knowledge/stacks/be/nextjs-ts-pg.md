# Next.js Route Handlers + Server Actions + Prisma + PostgreSQL Patterns
> Stack: Next.js 14+ App Router + TypeScript 5 + Prisma 5 + PostgreSQL 16
> Type: be
> Slug: nextjs-ts-pg
> Deployment: Railway + GitHub Actions CI/CD
>
> Copy to knowledge/L0-global/be-patterns.md during /onboard.
> This file covers all server-side concerns in a Next.js fullstack monorepo:
> Route Handlers (REST API), Server Actions (mutations), Prisma ORM, Auth, Deployment.

## §index — Section Map

| §   | Topic | Load when |
|-----|-------|-----------|
| §1  | Stack invariants | ALWAYS |
| §2  | Prisma schema (models) | Creating or modifying data models |
| §3  | Database client setup | First time wiring Prisma in a new module |
| §4  | Route Handlers (REST API) | Writing GET/POST/PUT/PATCH/DELETE endpoints |
| §5  | Server Actions (mutations) | Writing form submissions or server-triggered mutations |
| §6  | Zod validation | Validating any user input |
| §7  | Auth (NextAuth / Auth.js) | Writing protected routes or reading session |
| §8  | Query patterns | Filtered list queries, pagination, sorting |
| §9  | Transactions | Multi-table atomic writes |
| §10 | Migrations (Prisma) | DB schema changes |
| §11 | Common scenarios | File upload, webhooks, background jobs |
| §12 | Deployment (Railway + GitHub Actions) | Setting up CI/CD pipeline |
| §13 | RBAC — Roles & permissions | Any ticket that touches access control or adds a protected route |
| §14 | Security — Rate limiting & headers | Auth endpoints, sensitive mutations, or any new public endpoint |
| §15 | Anti-patterns | ALWAYS before writing any server code |

---

## §1 — Stack invariants

- **Prisma only** for all DB access — no raw SQL, no `$queryRaw` for CRUD, no other ORM
- **Route Handlers** in `app/api/` for REST-style endpoints consumed by external clients or client components
- **Server Actions** for mutations triggered directly from Server/Client Components (form submissions, button actions)
- **Zod** for all input validation — validate before any DB call, return 400 with structured error on failure
- **Auth.js (NextAuth v5)** for authentication — session via `auth()` helper, protection via `middleware.ts`
- `lib/db.ts` is the **single Prisma client instance** — never instantiate `PrismaClient` elsewhere
- Environment variable `DATABASE_URL` is server-only — never prefix with `NEXT_PUBLIC_`
- Railway handles production deploys — `prisma migrate deploy` runs as part of the start command

---

## §2 — Prisma schema (models)

```prisma
// prisma/schema.prisma

generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

// Every model must have these base fields
model Order {
  id        String      @id @default(cuid())
  createdAt DateTime    @default(now())
  updatedAt DateTime    @updatedAt
  deletedAt DateTime?   // soft-delete — add only when required

  // Business fields
  code      String      @unique
  status    OrderStatus @default(PENDING)
  total     Decimal     @db.Decimal(12, 2)

  // Relations
  customerId String
  customer   Customer @relation(fields: [customerId], references: [id])
  items      OrderItem[]

  @@map("orders")   // table name: snake_case plural
}

enum OrderStatus {
  PENDING
  CONFIRMED
  SHIPPED
  DELIVERED
  CANCELLED
}
```

**Rules:**
- `id`: always `String @id @default(cuid())` — never auto-increment INT
- `createdAt`/`updatedAt`: required on every model
- `deletedAt`: optional, only add when soft-delete is a business requirement
- `@@map`: always snake_case plural to match PostgreSQL convention
- Enums: SCREAMING_SNAKE_CASE

---

## §3 — Database client

```typescript
// lib/db.ts — singleton pattern required for Next.js hot-reload in dev

import { PrismaClient } from '@prisma/client'

const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined
}

export const db =
  globalForPrisma.prisma ??
  new PrismaClient({
    log: process.env.NODE_ENV === 'development' ? ['query', 'error', 'warn'] : ['error'],
  })

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = db
```

**Usage:**
```typescript
import { db } from '@/lib/db'

const orders = await db.order.findMany({ where: { status: 'PENDING' } })
```

---

## §4 — Route Handlers

```typescript
// app/api/orders/route.ts — collection endpoints (GET list, POST create)

import { NextRequest, NextResponse } from 'next/server'
import { db } from '@/lib/db'
import { auth } from '@/auth'
import { createOrderSchema } from '@/lib/validations/order'

export async function GET(request: NextRequest) {
  const session = await auth()
  if (!session) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })

  const { searchParams } = request.nextUrl
  const page = Number(searchParams.get('page') ?? 1)
  const limit = Number(searchParams.get('limit') ?? 20)

  const [data, total] = await db.$transaction([
    db.order.findMany({
      where: { deletedAt: null },
      orderBy: { createdAt: 'desc' },
      skip: (page - 1) * limit,
      take: limit,
      select: {
        id: true,
        code: true,
        status: true,
        total: true,
        createdAt: true,
        customer: { select: { id: true, name: true } },
      },
    }),
    db.order.count({ where: { deletedAt: null } }),
  ])

  return NextResponse.json({ data, total, page, limit })
}

export async function POST(request: NextRequest) {
  const session = await auth()
  if (!session) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })

  const body = await request.json()
  const parsed = createOrderSchema.safeParse(body)
  if (!parsed.success) {
    return NextResponse.json({ error: parsed.error.flatten() }, { status: 400 })
  }

  const order = await db.order.create({ data: parsed.data })
  return NextResponse.json(order, { status: 201 })
}
```

```typescript
// app/api/orders/[id]/route.ts — item endpoints (GET, PATCH, DELETE)

export async function GET(_req: NextRequest, { params }: { params: { id: string } }) {
  const order = await db.order.findUnique({
    where: { id: params.id, deletedAt: null },
    include: { items: true, customer: true },
  })
  if (!order) return NextResponse.json({ error: 'Not found' }, { status: 404 })
  return NextResponse.json(order)
}

export async function PATCH(request: NextRequest, { params }: { params: { id: string } }) {
  const session = await auth()
  if (!session) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })

  const body = await request.json()
  const parsed = updateOrderSchema.safeParse(body)
  if (!parsed.success) {
    return NextResponse.json({ error: parsed.error.flatten() }, { status: 400 })
  }

  const order = await db.order.update({
    where: { id: params.id },
    data: parsed.data,
  })
  return NextResponse.json(order)
}

export async function DELETE(_req: NextRequest, { params }: { params: { id: string } }) {
  // Soft delete — set deletedAt
  await db.order.update({
    where: { id: params.id },
    data: { deletedAt: new Date() },
  })
  return new NextResponse(null, { status: 204 })
}
```

---

## §5 — Server Actions

```typescript
// actions/order.ts (or collocated near the component that uses it)

'use server'

import { revalidatePath } from 'next/cache'
import { redirect } from 'next/navigation'
import { auth } from '@/auth'
import { db } from '@/lib/db'
import { createOrderSchema } from '@/lib/validations/order'

export type ActionResult<T = void> =
  | { success: true; data: T }
  | { success: false; error: string; fieldErrors?: Record<string, string[]> }

export async function createOrder(
  _prev: ActionResult,
  formData: FormData,
): Promise<ActionResult<{ id: string }>> {
  const session = await auth()
  if (!session) return { success: false, error: 'Unauthorized' }

  const raw = Object.fromEntries(formData)
  const parsed = createOrderSchema.safeParse(raw)
  if (!parsed.success) {
    return { success: false, error: 'Validation failed', fieldErrors: parsed.error.flatten().fieldErrors }
  }

  const order = await db.order.create({ data: { ...parsed.data, createdById: session.user.id } })

  revalidatePath('/orders')
  return { success: true, data: { id: order.id } }
}

export async function updateOrderStatus(id: string, status: string): Promise<ActionResult> {
  const session = await auth()
  if (!session) return { success: false, error: 'Unauthorized' }

  await db.order.update({ where: { id }, data: { status: status as any } })
  revalidatePath(`/orders/${id}`)
  return { success: true, data: undefined }
}
```

**Action result shape:**
```typescript
// Always return this shape — never throw from a Server Action
{ success: true; data: T }      // happy path
{ success: false; error: string; fieldErrors?: Record<string, string[]> }  // error path
```

---

## §6 — Zod validation

```typescript
// lib/validations/order.ts

import { z } from 'zod'

export const createOrderSchema = z.object({
  customerId: z.string().cuid('Invalid customer ID'),
  items: z.array(
    z.object({
      productId: z.string().cuid(),
      quantity: z.number().int().positive(),
      unitPrice: z.number().positive(),
    }),
  ).min(1, 'At least one item required'),
  notes: z.string().max(500).optional(),
})

export const updateOrderSchema = createOrderSchema.partial().extend({
  status: z.enum(['PENDING', 'CONFIRMED', 'SHIPPED', 'DELIVERED', 'CANCELLED']).optional(),
})

export type CreateOrderInput = z.infer<typeof createOrderSchema>
export type UpdateOrderInput = z.infer<typeof updateOrderSchema>
```

**Rules:**
- One Zod schema file per module in `lib/validations/[module].ts`
- Export both schema and inferred types from the same file
- `safeParse()` in Route Handlers (don't throw), `parse()` in Server Actions caught by try/catch

---

## §7 — Auth (NextAuth / Auth.js v5)

```typescript
// auth.ts (project root)
import NextAuth from 'next-auth'
import Credentials from 'next-auth/providers/credentials'
import { db } from '@/lib/db'
import bcrypt from 'bcryptjs'

export const { handlers, auth, signIn, signOut } = NextAuth({
  providers: [
    Credentials({
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' },
      },
      authorize: async ({ email, password }) => {
        const user = await db.user.findUnique({ where: { email: email as string } })
        if (!user || !await bcrypt.compare(password as string, user.passwordHash)) return null
        return { id: user.id, email: user.email, name: user.name, role: user.role }
      },
    }),
  ],
  callbacks: {
    jwt({ token, user }) {
      if (user) token.role = (user as any).role
      return token
    },
    session({ session, token }) {
      session.user.id = token.sub!
      session.user.role = token.role as string
      return session
    },
  },
})
```

```typescript
// middleware.ts — protect routes
import { auth } from '@/auth'
import { NextResponse } from 'next/server'

export default auth((req) => {
  const isLoggedIn = !!req.auth
  const isAuthRoute = req.nextUrl.pathname.startsWith('/login')

  if (!isLoggedIn && !isAuthRoute) {
    return NextResponse.redirect(new URL('/login', req.url))
  }
  return NextResponse.next()
})

export const config = {
  matcher: ['/((?!api/auth|_next/static|_next/image|favicon.ico).*)'],
}
```

**Reading session:**
```typescript
// In Server Component or Server Action
import { auth } from '@/auth'
const session = await auth()
if (!session?.user) redirect('/login')

// In Route Handler
const session = await auth()
if (!session) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
```

---

## §8 — Query patterns (filtered list + pagination)

```typescript
// Standard list query with filters, search, pagination
async function listOrders(params: {
  status?: OrderStatus
  customerId?: string
  search?: string
  page?: number
  limit?: number
  sortBy?: 'createdAt' | 'total'
  sortDir?: 'asc' | 'desc'
}) {
  const { status, customerId, search, page = 1, limit = 20, sortBy = 'createdAt', sortDir = 'desc' } = params

  const where: Prisma.OrderWhereInput = {
    deletedAt: null,
    ...(status && { status }),
    ...(customerId && { customerId }),
    ...(search && {
      OR: [
        { code: { contains: search, mode: 'insensitive' } },
        { customer: { name: { contains: search, mode: 'insensitive' } } },
      ],
    }),
  }

  const [data, total] = await db.$transaction([
    db.order.findMany({
      where,
      orderBy: { [sortBy]: sortDir },
      skip: (page - 1) * limit,
      take: limit,
      select: { id: true, code: true, status: true, total: true, createdAt: true },
    }),
    db.order.count({ where }),
  ])

  return { data, total, page, limit, totalPages: Math.ceil(total / limit) }
}
```

---

## §9 — Transactions

```typescript
// Sequential transaction (list of operations)
const [order, _] = await db.$transaction([
  db.order.create({ data: orderData }),
  db.inventory.update({ where: { id: productId }, data: { stock: { decrement: qty } } }),
])

// Interactive transaction (with conditional logic)
const result = await db.$transaction(async (tx) => {
  const inventory = await tx.inventory.findUnique({ where: { productId } })
  if (!inventory || inventory.stock < qty) throw new Error('Insufficient stock')

  const order = await tx.order.create({ data: orderData })
  await tx.inventory.update({
    where: { productId },
    data: { stock: { decrement: qty } },
  })
  return order
})
```

---

## §10 — Migrations (Prisma)

```bash
# Development — creates migration file + applies to dev DB
npx prisma migrate dev --name add_order_status_column

# Production (Railway) — applies pending migrations without creating new ones
npx prisma migrate deploy

# After schema change, always regenerate client
npx prisma generate
```

**Rules:**
- Never edit a migration file after it has been applied to any environment
- Additive-only in production: add columns/tables, never rename/drop without a deprecation sprint
- Railway runs `npx prisma migrate deploy` automatically via the start command (see §12)
- Run `npx prisma generate` in CI before build step

---

## §11 — Common scenarios

### File upload (with Railway Volumes or S3-compatible)

```typescript
// Route Handler for file upload
export async function POST(request: NextRequest) {
  const formData = await request.formData()
  const file = formData.get('file') as File
  if (!file) return NextResponse.json({ error: 'No file' }, { status: 400 })

  // Railway Volume: save to /data (persistent volume mounted at /data)
  // OR: use AWS S3 / Cloudflare R2 — store file, return URL
  const buffer = await file.arrayBuffer()
  const url = await uploadToStorage(Buffer.from(buffer), file.name)

  return NextResponse.json({ url })
}
```

### Webhook receiver

```typescript
export async function POST(request: NextRequest) {
  const signature = request.headers.get('x-webhook-signature')
  const body = await request.text()

  if (!verifySignature(body, signature)) {
    return NextResponse.json({ error: 'Invalid signature' }, { status: 401 })
  }

  const event = JSON.parse(body)
  // process event async — return 200 immediately
  void processWebhookEvent(event)
  return NextResponse.json({ received: true })
}
```

---

## §12 — Deployment (Railway + GitHub Actions)

### railway.toml

```toml
# railway.toml — place at project root

[build]
builder = "NIXPACKS"
buildCommand = "npx prisma generate && npm run build"

[deploy]
startCommand = "npx prisma migrate deploy && npm start"
healthcheckPath = "/api/health"
healthcheckTimeout = 300
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3
```

### Environment variables (Railway dashboard)

```
DATABASE_URL          = postgresql://... (Railway provides this automatically when you add PostgreSQL)
NEXTAUTH_SECRET       = <random 32-char string>
NEXTAUTH_URL          = https://your-app.up.railway.app
NODE_ENV              = production
```

**Rules:**
- `DATABASE_URL` is auto-injected by Railway when PostgreSQL service is linked — never hardcode
- All secrets set in Railway environment, never in `.env` committed to git
- `.env.local` for local dev only — always in `.gitignore`

### GitHub Actions CI (`.github/workflows/ci.yml`)

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm

      - run: npm ci
      - run: npx prisma generate
      - run: npx tsc --noEmit          # type check
      - run: npm run lint               # ESLint
      # - run: npm test                # unit tests (add when test suite exists)
```

### Deploy flow (Railway auto-deploy)

```
developer pushes to develop →
  GitHub Actions CI runs (typecheck + lint) →
    if CI passes → Railway detects push → builds and deploys to staging automatically

developer merges PR to main →
  GitHub Actions CI runs →
    if CI passes → Railway detects push to main → deploys to production automatically

Railway runs on deploy:
  1. npx prisma generate
  2. npm run build
  3. npx prisma migrate deploy  ← applies pending DB migrations
  4. npm start
```

### Health check endpoint

```typescript
// app/api/health/route.ts
import { NextResponse } from 'next/server'
import { db } from '@/lib/db'

export async function GET() {
  try {
    await db.$queryRaw`SELECT 1`
    return NextResponse.json({ status: 'ok', db: 'connected' })
  } catch {
    return NextResponse.json({ status: 'error', db: 'disconnected' }, { status: 503 })
  }
}
```

---

## §13 — RBAC — Roles & Permissions

### Prisma schema

```prisma
model User {
  id           String   @id @default(cuid())
  email        String   @unique
  passwordHash String
  name         String
  role         UserRole @default(USER)
  createdAt    DateTime @default(now())
  updatedAt    DateTime @updatedAt
  deletedAt    DateTime?

  @@map("users")
}

enum UserRole {
  ADMIN
  MANAGER
  USER
}
// Extend roles per domain: ADMIN | HR_MANAGER | MANAGER | EMPLOYEE for HRM
// ADMIN | MANAGER | CASHIER | WAREHOUSE for POS
// ADMIN | SELLER | CUSTOMER | SUPPORT for ecommerce
```

### Role check in Route Handlers

```typescript
// lib/auth-helpers.ts — reusable guards

import { auth } from '@/auth'
import { NextResponse } from 'next/server'

export async function requireAuth() {
  const session = await auth()
  if (!session?.user) {
    return { session: null, error: NextResponse.json({ error: 'Unauthorized' }, { status: 401 }) }
  }
  return { session, error: null }
}

export async function requireRole(allowedRoles: string[]) {
  const { session, error } = await requireAuth()
  if (error) return { session: null, error }
  if (!allowedRoles.includes(session!.user.role)) {
    return { session: null, error: NextResponse.json({ error: 'Forbidden' }, { status: 403 }) }
  }
  return { session, error: null }
}
```

```typescript
// Usage in Route Handler
export async function DELETE(_req: NextRequest, { params }: { params: { id: string } }) {
  const { session, error } = await requireRole(['ADMIN'])
  if (error) return error

  await db.user.update({ where: { id: params.id }, data: { deletedAt: new Date() } })
  return new NextResponse(null, { status: 204 })
}
```

### Row-level security — data scoped to current user

```typescript
// ALWAYS filter by session user — never trust userId from request body/params
export async function GET(request: NextRequest) {
  const session = await auth()
  if (!session) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })

  const isAdmin = session.user.role === 'ADMIN'

  const orders = await db.order.findMany({
    where: {
      deletedAt: null,
      // Admin sees all; regular user sees only their own
      ...(isAdmin ? {} : { userId: session.user.id }),
    },
  })

  return NextResponse.json(orders)
}
```

### Manager sees team only (department/org-scoped queries)

```typescript
// HR Manager pattern — scoped by department when not admin
const isAdmin = session.user.role === 'ADMIN'
const isHRManager = session.user.role === 'HR_MANAGER'

const employees = await db.employee.findMany({
  where: {
    deletedAt: null,
    ...(isAdmin || isHRManager
      ? {} // sees all
      : { managerId: session.user.employeeId }), // manager sees only direct reports
  },
})
```

### Auth.js session — extend with role and employeeId

```typescript
// auth.ts callbacks (add employeeId to session if needed)
callbacks: {
  jwt({ token, user }) {
    if (user) {
      token.role = (user as any).role
      token.employeeId = (user as any).employeeId // if domain has employee profile
    }
    return token
  },
  session({ session, token }) {
    session.user.id = token.sub!
    session.user.role = token.role as string
    session.user.employeeId = token.employeeId as string | undefined
    return session
  },
},
```

---

## §14 — Security — Rate Limiting & Headers

### Rate limiting with @upstash/ratelimit (recommended for Railway)

```bash
npm install @upstash/ratelimit @upstash/redis
```

```typescript
// lib/rate-limit.ts
import { Ratelimit } from '@upstash/ratelimit'
import { Redis } from '@upstash/redis'

// Requires: UPSTASH_REDIS_REST_URL + UPSTASH_REDIS_REST_TOKEN in Railway env
export const authRateLimit = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(5, '15 m'), // 5 attempts per 15 min per IP
  analytics: true,
  prefix: 'ratelimit:auth',
})

export const apiRateLimit = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(100, '1 m'), // 100 req/min per IP
  prefix: 'ratelimit:api',
})
```

```typescript
// Usage on login / register / password-reset endpoints
export async function POST(request: NextRequest) {
  const ip = request.headers.get('x-forwarded-for') ?? '127.0.0.1'
  const { success, limit, remaining, reset } = await authRateLimit.limit(ip)

  if (!success) {
    return NextResponse.json(
      { error: 'Too many attempts. Try again later.' },
      {
        status: 429,
        headers: {
          'X-RateLimit-Limit': String(limit),
          'X-RateLimit-Remaining': String(remaining),
          'X-RateLimit-Reset': String(reset),
          'Retry-After': String(Math.ceil((reset - Date.now()) / 1000)),
        },
      },
    )
  }

  // ... proceed with login logic
}
```

### Alternative: simple in-memory rate limiter (no Redis, dev-only)

```typescript
// For development or projects without Upstash — NOT for production
import { LRUCache } from 'lru-cache'

const rateLimit = new LRUCache<string, number[]>({ max: 500, ttl: 15 * 60 * 1000 })

export function checkRateLimit(ip: string, limit = 5): boolean {
  const now = Date.now()
  const windowStart = now - 15 * 60 * 1000
  const hits = (rateLimit.get(ip) ?? []).filter(t => t > windowStart)
  if (hits.length >= limit) return false
  rateLimit.set(ip, [...hits, now])
  return true
}
```

### Security headers in next.config.ts

```typescript
// next.config.ts
const securityHeaders = [
  { key: 'X-DNS-Prefetch-Control', value: 'on' },
  { key: 'X-Frame-Options', value: 'SAMEORIGIN' },
  { key: 'X-Content-Type-Options', value: 'nosniff' },
  { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
  {
    key: 'Content-Security-Policy',
    value: [
      "default-src 'self'",
      "script-src 'self' 'unsafe-inline' 'unsafe-eval'", // tighten per project
      "style-src 'self' 'unsafe-inline'",
      "img-src 'self' data: blob: https:",
      "font-src 'self'",
      "connect-src 'self'",
    ].join('; '),
  },
]

const nextConfig = {
  async headers() {
    return [{ source: '/(.*)', headers: securityHeaders }]
  },
}
export default nextConfig
```

### DDoS note

Railway provides basic L3/L4 DDoS protection out of the box.
For L7 application-level protection, add Cloudflare in front of Railway:
1. Set Railway app domain (e.g. `app.railway.app`)
2. Add custom domain in Cloudflare → proxy enabled (orange cloud)
3. Enable Cloudflare WAF (free tier covers most common attacks)

Rate limiting (§14 above) handles burst/brute-force at the application layer.

---

## §15 — Anti-patterns

- **Never instantiate `PrismaClient` outside `lib/db.ts`** — causes connection pool exhaustion in dev due to hot-reload
- **Never use `$queryRaw` for regular CRUD** — use typed Prisma methods; `$queryRaw` only for complex aggregations not expressible in Prisma
- **Never expose `DATABASE_URL` to the client** — no `NEXT_PUBLIC_DATABASE_URL` ever
- **Never skip Zod validation on user input** — always `safeParse()` before DB call
- **Never throw inside a Server Action** — return `{ success: false, error }` shape instead; uncaught throws crash silently in some RSC contexts
- **Never use `redirect()` inside try/catch in Server Actions** — `redirect()` works by throwing; catching it breaks navigation
- **Never edit applied migration files** — delete your local DB and re-run `prisma migrate dev` if needed during development
- **Never run `prisma migrate dev` on the production database** — only `prisma migrate deploy`
- **Never store JWT or session tokens in `localStorage`** — Auth.js uses httpOnly cookies by default; keep it that way
- **Never add `NEXT_PUBLIC_` prefix to secrets** — those values are bundled into the client JS
