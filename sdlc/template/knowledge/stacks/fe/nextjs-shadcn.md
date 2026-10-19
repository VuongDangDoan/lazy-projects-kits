# Next.js App Router + shadcn/ui Patterns
> Stack: Next.js 14+ App Router + TypeScript 5 + shadcn/ui + Tailwind CSS
> Type: fe
> Slug: nextjs-shadcn
>
> Copy to knowledge/L0-global/fe-patterns.md during /onboard.
> This file covers all client-side concerns in a Next.js fullstack monorepo:
> App Router pages, Server/Client Components, shadcn/ui, forms, data fetching.

## §index — Section Map

| §   | Topic | Load when |
|-----|-------|-----------|
| §1  | Stack invariants | ALWAYS |
| §2  | File & folder structure | Creating a new module/feature |
| §3  | Server Components (data fetching) | Fetching data in pages or layouts |
| §4  | Client Components | Interactive UI, forms, event handlers |
| §5  | Forms (react-hook-form + zod) | Building any input form |
| §6  | Tables / Lists | Building data tables with filters and pagination |
| §7  | Routing & navigation | Adding pages, protected routes, redirects |
| §8  | shadcn/ui component usage | Using or composing UI components |
| §9  | Permissions / RBAC | Hiding or disabling UI based on role |
| §10 | Modals & Drawers | State-driven dialogs and slide-over panels |
| §11 | Common scenarios | Image upload, toast notifications, loading states |
| §15 | Anti-patterns | ALWAYS before writing any component |

---

## §1 — Stack invariants

- **App Router only** — no Pages Router. All routes under `app/`
- **Server Components by default** — add `'use client'` only when needed (event handlers, hooks, browser APIs)
- **shadcn/ui** for all UI primitives — import from `@/components/ui/[component]`
- **Tailwind CSS** for all styling — no CSS Modules, no `style={{}}`, no styled-components
- **TanStack Query v5** (`@tanstack/react-query`) for client-side data fetching in Client Components
- **react-hook-form + zod** for all forms — no uncontrolled inputs, no manual `useState` for form fields
- **Server Actions** for form mutations — prefer over `fetch()` to an API route from a form
- **`cn()` utility** from `@/lib/utils` for conditional Tailwind classes — never string concatenation

---

## §2 — File & folder structure

```
app/
  (auth)/                        ← route group — shares auth layout
    login/
      page.tsx
  (dashboard)/                   ← route group — shares dashboard layout
    layout.tsx                   ← sidebar + header wrapper
    orders/
      page.tsx                   ← list page (Server Component)
      [id]/
        page.tsx                 ← detail page (Server Component)
      _components/               ← co-located components (not routable)
        orders-table.tsx
        order-filters.tsx
        create-order-dialog.tsx

components/
  ui/                            ← shadcn generated components (never edit manually)
    button.tsx
    dialog.tsx
    form.tsx
    ...
  [shared-component].tsx         ← shared components used across modules

lib/
  utils.ts                       ← cn() and shared utilities
  validations/
    order.ts                     ← Zod schemas (shared with Server Actions)

hooks/
  use-orders.ts                  ← TanStack Query hooks (client-side)
  use-debounce.ts                ← utility hooks
```

**Rules:**
- Page-specific components go in `app/[module]/_components/` (not imported outside that module)
- Shared components go in `components/` (imported by multiple modules)
- Never edit files in `components/ui/` — re-run `npx shadcn@latest add` to update them
- `_components/`, `_hooks/`, `_lib/` prefixes make folders non-routable in App Router

---

## §3 — Server Components (data fetching)

```typescript
// app/(dashboard)/orders/page.tsx — Server Component (default)

import { db } from '@/lib/db'
import { auth } from '@/auth'
import { redirect } from 'next/navigation'
import { OrdersTable } from './_components/orders-table'
import { OrderFilters } from './_components/order-filters'

interface Props {
  searchParams: { page?: string; status?: string; search?: string }
}

export default async function OrdersPage({ searchParams }: Props) {
  const session = await auth()
  if (!session) redirect('/login')

  const page = Number(searchParams.page ?? 1)
  const status = searchParams.status
  const search = searchParams.search

  const [orders, total] = await Promise.all([
    db.order.findMany({
      where: {
        deletedAt: null,
        ...(status && { status: status as any }),
        ...(search && { code: { contains: search, mode: 'insensitive' } }),
      },
      orderBy: { createdAt: 'desc' },
      skip: (page - 1) * 20,
      take: 20,
      include: { customer: { select: { name: true } } },
    }),
    db.order.count({ where: { deletedAt: null } }),
  ])

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Orders</h1>
      </div>
      <OrderFilters />
      <OrdersTable orders={orders} total={total} page={page} />
    </div>
  )
}
```

**Rules for Server Components:**
- Always `await auth()` at the top of protected pages
- Use Prisma directly — no need to go through an API route
- Pass data down as props to Client Components
- Use `searchParams` for filter/pagination state — no `useState` needed
- `loading.tsx` in the same folder automatically wraps the page in `<Suspense>`

---

## §4 — Client Components

```typescript
// app/(dashboard)/orders/_components/orders-table.tsx
'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'

interface Order {
  id: string
  code: string
  status: string
  total: number
  customer: { name: string }
  createdAt: Date
}

interface Props {
  orders: Order[]
  total: number
  page: number
}

export function OrdersTable({ orders, total, page }: Props) {
  const router = useRouter()

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Code</TableHead>
            <TableHead>Customer</TableHead>
            <TableHead>Status</TableHead>
            <TableHead className="text-right">Total</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {orders.map((order) => (
            <TableRow
              key={order.id}
              className="cursor-pointer hover:bg-muted/50"
              onClick={() => router.push(`/orders/${order.id}`)}
            >
              <TableCell className="font-mono">{order.code}</TableCell>
              <TableCell>{order.customer.name}</TableCell>
              <TableCell>
                <Badge variant={order.status === 'PENDING' ? 'secondary' : 'default'}>
                  {order.status}
                </Badge>
              </TableCell>
              <TableCell className="text-right">${Number(order.total).toFixed(2)}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}
```

**When to add `'use client'`:**
- Component has `onClick`, `onChange`, `onSubmit`, or any event handler
- Component uses `useState`, `useEffect`, `useRef`, or any hook
- Component uses browser APIs (`window`, `localStorage`, `navigator`)
- Component uses `useRouter`, `useSearchParams`, `usePathname`

---

## §5 — Forms (react-hook-form + zod + Server Actions)

```typescript
// app/(dashboard)/orders/_components/create-order-dialog.tsx
'use client'

import { useActionState, useTransition } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { createOrder } from '@/actions/order'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { toast } from 'sonner'

const formSchema = z.object({
  customerId: z.string().min(1, 'Customer is required'),
  notes: z.string().optional(),
})

type FormValues = z.infer<typeof formSchema>

export function CreateOrderDialog() {
  const [open, setOpen] = useState(false)
  const [isPending, startTransition] = useTransition()

  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: { customerId: '', notes: '' },
  })

  function onSubmit(values: FormValues) {
    startTransition(async () => {
      const result = await createOrder(values)
      if (result.success) {
        toast.success('Order created')
        form.reset()
        setOpen(false)
      } else {
        toast.error(result.error)
        if (result.fieldErrors) {
          Object.entries(result.fieldErrors).forEach(([field, errors]) => {
            form.setError(field as any, { message: errors[0] })
          })
        }
      }
    })
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>New Order</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create Order</DialogTitle>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="customerId"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Customer</FormLabel>
                  <FormControl>
                    <Input placeholder="Customer ID" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <Button type="submit" disabled={isPending} className="w-full">
              {isPending ? 'Creating...' : 'Create Order'}
            </Button>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}
```

---

## §6 — Tables with filters and pagination

```typescript
// app/(dashboard)/orders/_components/order-filters.tsx
'use client'

import { useRouter, useSearchParams, usePathname } from 'next/navigation'
import { useCallback } from 'react'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { useDebounce } from '@/hooks/use-debounce'

export function OrderFilters() {
  const router = useRouter()
  const pathname = usePathname()
  const searchParams = useSearchParams()

  const updateParam = useCallback(
    (key: string, value: string) => {
      const params = new URLSearchParams(searchParams.toString())
      if (value) {
        params.set(key, value)
      } else {
        params.delete(key)
      }
      params.delete('page') // reset to page 1 on filter change
      router.replace(`${pathname}?${params.toString()}`)
    },
    [router, pathname, searchParams],
  )

  const [search, setSearch] = useState(searchParams.get('search') ?? '')
  const debouncedSearch = useDebounce(search, 300)

  useEffect(() => {
    updateParam('search', debouncedSearch)
  }, [debouncedSearch, updateParam])

  return (
    <div className="flex gap-3">
      <Input
        placeholder="Search orders..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="max-w-xs"
      />
      <Select
        value={searchParams.get('status') ?? 'all'}
        onValueChange={(v) => updateParam('status', v === 'all' ? '' : v)}
      >
        <SelectTrigger className="w-40">
          <SelectValue placeholder="Status" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All statuses</SelectItem>
          <SelectItem value="PENDING">Pending</SelectItem>
          <SelectItem value="CONFIRMED">Confirmed</SelectItem>
          <SelectItem value="SHIPPED">Shipped</SelectItem>
        </SelectContent>
      </Select>
    </div>
  )
}
```

**Pagination pattern:**
```typescript
// URL-based pagination — no useState needed
// Page state lives in searchParams, read by Server Component, no client hydration needed

// Pagination component (Client Component)
'use client'
import { useRouter, useSearchParams, usePathname } from 'next/navigation'
import { Button } from '@/components/ui/button'

export function Pagination({ total, limit = 20 }: { total: number; limit?: number }) {
  const router = useRouter()
  const pathname = usePathname()
  const searchParams = useSearchParams()
  const page = Number(searchParams.get('page') ?? 1)
  const totalPages = Math.ceil(total / limit)

  const go = (p: number) => {
    const params = new URLSearchParams(searchParams.toString())
    params.set('page', String(p))
    router.push(`${pathname}?${params.toString()}`)
  }

  return (
    <div className="flex items-center gap-2">
      <Button variant="outline" size="sm" onClick={() => go(page - 1)} disabled={page <= 1}>Previous</Button>
      <span className="text-sm text-muted-foreground">Page {page} of {totalPages}</span>
      <Button variant="outline" size="sm" onClick={() => go(page + 1)} disabled={page >= totalPages}>Next</Button>
    </div>
  )
}
```

---

## §7 — Routing & navigation

```typescript
// Programmatic navigation (Client Component)
import { useRouter } from 'next/navigation'
const router = useRouter()
router.push('/orders/new')
router.replace('/orders')  // no history entry
router.refresh()            // re-fetch Server Component data without full navigation

// Link (Server or Client Component)
import Link from 'next/link'
<Link href={`/orders/${id}`}>View</Link>

// Redirect (Server Component / Server Action)
import { redirect } from 'next/navigation'
redirect('/login')          // inside Server Component, Layout, or Server Action

// Protected layout — check session once for all child routes
// app/(dashboard)/layout.tsx
import { auth } from '@/auth'
import { redirect } from 'next/navigation'

export default async function DashboardLayout({ children }: { children: React.ReactNode }) {
  const session = await auth()
  if (!session) redirect('/login')
  return <>{children}</>
}
```

---

## §8 — shadcn/ui component usage

```bash
# Install a component
npx shadcn@latest add button
npx shadcn@latest add dialog form input table badge select toast

# Never edit files in components/ui/ manually
# To customize: create a wrapper component in components/ that uses the ui/ primitive
```

```typescript
// Correct: wrap and extend, never modify ui/ directly
// components/status-badge.tsx
import { Badge } from '@/components/ui/badge'
import { OrderStatus } from '@prisma/client'

const statusVariant: Record<OrderStatus, 'default' | 'secondary' | 'destructive'> = {
  PENDING: 'secondary',
  CONFIRMED: 'default',
  SHIPPED: 'default',
  DELIVERED: 'default',
  CANCELLED: 'destructive',
}

export function StatusBadge({ status }: { status: OrderStatus }) {
  return <Badge variant={statusVariant[status]}>{status}</Badge>
}
```

**Toast notifications:**
```typescript
// Use sonner (ships with shadcn)
import { toast } from 'sonner'

toast.success('Order created')
toast.error('Something went wrong')
toast.loading('Saving...')
```

---

## §9 — Permissions / RBAC

```typescript
// Server Component — hide sections by role
const session = await auth()
const isAdmin = session?.user.role === 'ADMIN'

return (
  <div>
    <OrdersTable orders={orders} />
    {isAdmin && <AdminActionsPanel />}
  </div>
)

// Client Component — disable actions by role
'use client'
import { useSession } from 'next-auth/react'

export function OrderActions({ orderId }: { orderId: string }) {
  const { data: session } = useSession()
  const canDelete = session?.user.role === 'ADMIN'

  return (
    <Button variant="destructive" disabled={!canDelete} onClick={...}>
      Delete
    </Button>
  )
}
```

---

## §10 — Modals & Drawers

```typescript
// Dialog pattern — controlled via useState
'use client'
import { useState } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'

export function EditOrderDialog({ order }: { order: Order }) {
  const [open, setOpen] = useState(false)

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">Edit</Button>
      </DialogTrigger>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>Edit Order {order.code}</DialogTitle>
        </DialogHeader>
        <EditOrderForm order={order} onSuccess={() => setOpen(false)} />
      </DialogContent>
    </Dialog>
  )
}

// Confirmation dialog pattern
import { AlertDialog, AlertDialogAction, AlertDialogCancel,
         AlertDialogContent, AlertDialogDescription, AlertDialogFooter,
         AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from '@/components/ui/alert-dialog'

export function DeleteOrderButton({ id }: { id: string }) {
  return (
    <AlertDialog>
      <AlertDialogTrigger asChild>
        <Button variant="destructive" size="sm">Delete</Button>
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Delete this order?</AlertDialogTitle>
          <AlertDialogDescription>This action cannot be undone.</AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Cancel</AlertDialogCancel>
          <AlertDialogAction onClick={() => deleteOrder(id)}>Delete</AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}
```

---

## §11 — Common scenarios

### Loading state with Suspense

```typescript
// app/(dashboard)/orders/loading.tsx — automatic Suspense fallback
import { Skeleton } from '@/components/ui/skeleton'

export default function Loading() {
  return (
    <div className="space-y-4">
      <Skeleton className="h-8 w-48" />
      <Skeleton className="h-64 w-full" />
    </div>
  )
}
```

### Optimistic updates with TanStack Query (client-side)

```typescript
// hooks/use-orders.ts — use when page.tsx can't be Server Component (rare)
'use client'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

export function useOrders(params: OrderParams) {
  return useQuery({
    queryKey: ['orders', params],
    queryFn: () => fetch(`/api/orders?${new URLSearchParams(params as any)}`).then(r => r.json()),
  })
}

export function useUpdateOrderStatus() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      fetch(`/api/orders/${id}`, {
        method: 'PATCH',
        body: JSON.stringify({ status }),
        headers: { 'Content-Type': 'application/json' },
      }).then(r => r.json()),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['orders'] }),
  })
}
```

### Next.js Image

```typescript
import Image from 'next/image'

<Image
  src="/images/logo.png"
  alt="Logo"
  width={120}
  height={40}
  priority  // add for above-the-fold images
/>
```

---

## §15 — Anti-patterns

- **Never add `'use client'` to a layout or a page that only reads data** — making a Server Component a Client Component forces its entire subtree to be client-side
- **Never call `db` (Prisma) inside a Client Component** — Prisma is server-only; it will fail at build time
- **Never use `useState` for search/filter/pagination** — store these in URL `searchParams` so the Server Component re-runs with fresh data on navigation
- **Never call a Route Handler from a Server Component** — just call `db` directly; the HTTP round-trip is wasteful
- **Never use `fetch()` in a Server Component to call your own API routes** — call the service/db layer directly
- **Never store auth tokens in `localStorage` or `sessionStorage`** — Auth.js uses httpOnly cookies; never override this
- **Never use `useEffect` to fetch data** — use TanStack Query or Server Components; `useEffect` fetch is an anti-pattern in App Router
- **Never edit `components/ui/` files manually** — they are shadcn-managed; re-add via CLI to update
- **Never use `router.push()` after a Server Action to refresh data** — use `revalidatePath()` inside the action instead; the page will re-render automatically
- **Never import from `next/router`** — use `next/navigation` (App Router); `next/router` is Pages Router only
