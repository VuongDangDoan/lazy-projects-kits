---
description: Nontech project setup — 1 language question + 3 plain questions, auto-selects stack, applies industry template, writes project.config.json and runs scripts/scaffold.sh.
argument-hint: (no arguments — interactive)
---

# /quickstart — Nontech Project Setup

Simplified onboarding for non-technical users. $ARGUMENTS is ignored — the flow is interactive.
Same engine as `/onboard` (writes `project.config.json`, runs `scripts/scaffold.sh`) with the
technical decisions made automatically.

| /quickstart | /onboard |
|---|---|
| Nontech user, stack auto-selected (Next.js + Railway) | Tech user, full control (9 questions) |
| Industry template auto-detected | No templates |

---

## Pre-flight — block on active work (MANDATORY, same as /onboard)

Before anything destructive, read `project.config.json`, `knowledge/L3-session/active-context.md`,
and `tasks/kanban.md` (if present). If any ticket is in progress or active-context holds real
session content, STOP:

```
Không thể tiếp tục: workspace đang có công việc dở dang.
  [list tickets / active-context state]
Hoàn thành trước, hoặc trả lời `abandon` để bỏ và làm mới.
```

Wait for explicit resolution. Never archive over active work silently.

---

## Phase Q — Interview

First, ONE explicit language question (never infer):

```
Bạn muốn trao đổi bằng Tiếng Việt hay English? (vi / en)
```

Then the 3 plain questions, in the chosen language (all in one message):

```
1. Hệ thống của bạn làm gì? (mô tả bằng lời thường)
   Ví dụ: "Quản lý nhân sự cho công ty 50 người" · "Shop online bán quần áo"
2. Ai sẽ dùng?  a) Nhân viên nội bộ  b) Khách hàng bên ngoài  c) Cả hai
3. Tên hệ thống?  Ví dụ: "HRM Pro", "FashionShop"
```

Wait for all answers before proceeding.

---

## Phase A — Auto-Configuration

- **Stack (always):** Next.js 14+ App Router + TypeScript + Prisma + PostgreSQL ·
  Railway + GitHub Actions · Auth.js (NextAuth v5) · shadcn/ui + Tailwind. Single repo (BE = FE).
- **Short code — ONE rule:** take the first letter of each word, uppercase.
  If the result is shorter than 2 chars (single-word name), take the first 3 letters uppercase.
  Examples: "Fashion Shop" → `FS` · "HRM Pro" → `HP` · "MedBook" → `MED` · "POS Manager Pro" → `PMP`.
- **Repo name:** project name in kebab-case, lowercase, max 30 chars ("HRM Pro" → `hrm-pro`).
- **Language:** the answer to the explicit language question above.
- **Modules:** from the template if one is used (Phase T); else "Auth" + modules inferred from Q1.
- **check_cmd:** `npx --no-install tsc --noEmit -p tsconfig.json`.

---

## Phase T — Template Detection

Only these 3 templates exist (see `templates/README.md` — booking/crm are NOT shipped; never offer them):

| Keywords in Q1 | Template |
|---|---|
| nhân sự / HR / employee / chấm công / nghỉ phép / lương / payroll | `templates/hrm/` |
| bán hàng / POS / quầy / cashier / kho / thu ngân | `templates/pos/` |
| shop / thương mại / ecommerce / đơn hàng / sản phẩm / product / order | `templates/ecommerce/` |
| No match | Custom — empty scaffold |

If matched, offer it ("Dùng template có sẵn không? yes/no") — modules, business rules, and RBAC
roles come pre-filled. Record `template_used`.

---

## Phase S — Scope Summary (explicit confirmation)

```
## Tóm tắt cấu hình
Dự án:    [name] ([SHORT_CODE])    Repo: [repo-name]
Stack:    Next.js + PostgreSQL + Railway (tự động)
Template: [hrm / pos / ecommerce / không]    Ngôn ngữ: [vi/en]
Modules:  [list]
Sẽ lưu trữ (archive) dữ liệu dự án cũ: [real count từ find | wc -l] files
Tiếp tục không? (proceed / có)
```

Wait for confirmation.

---

## Phase B — Build the Workspace (same engine as /onboard)

1. **Archive** any previous project artifacts — run the `/onboard` Phase 3 archive block
   exactly (real `mv` per path, no error suppression; `find _source -maxdepth 1 -type l -delete`).
2. **Write `project.config.json`** — full shape, `initialized: true`:
   - project: name (Q3), short_code (Phase A), language (explicit question)
   - repos.be: `{ name: [repo-name], stack: "Next.js fullstack + TypeScript + PostgreSQL", check_cmd: "npx --no-install tsc --noEmit -p tsconfig.json" }`; fe/mobile names empty
   - modules: slug (kebab), name (Title), br_prefix (`BR-` + first 3 letters uppercase, de-duplicated)
3. **Scaffold:** `scripts/scaffold.sh --force DOMAIN="[from Q1]" DATABASE=PostgreSQL CODEBASE_STATE=greenfield`
4. **Patterns overlay (Next.js fullstack needs both):** copy `knowledge/stacks/be/nextjs-ts-pg.md`
   → `knowledge/L0-global/be-patterns.md` AND `knowledge/stacks/fe/nextjs-shadcn.md` → `fe-patterns.md`.
5. **Template application** (if `template_used`): `templates/[type]/brd.md` → `docs/brd.md`;
   split `templates/[type]/domain.md` by `## Module:` headers into `knowledge/L1-domain/[slug]-domain.md`.
6. **Verify:** `grep -rn '{{' CLAUDE.md AGENTS.md knowledge/` must return nothing.

---

## Phase C — Completion Summary (in the user's language)

```
## Thiết lập hoàn tất — [name]

Bước tiếp theo:
  1. Tạo repo code và chạy lệnh symlink (1 lần, trong terminal):
       cd [workspace-path] && ln -s ../../[repo-name] _source/[repo-name]
  2. Mô tả tính năng đầu tiên:  /build "Auth & RBAC — đăng nhập và phân quyền"
     (nền tảng bảo mật — phải xây trước mọi tính năng khác)
  3. Xem tiến độ:  /status

Chi phí tham khảo (CHỈ MANG TÍNH CHẤT ƯỚC LƯỢNG — kiểm tra giá hiện tại của từng dịch vụ):
  Claude Code + Railway + GitHub: thường vài chục USD/tháng cho app nhỏ.
  /devops sẽ hướng dẫn thiết lập deploy khi bạn sẵn sàng.
```

Note: never ask the user to paste any password, token, or key into this chat at any point —
deployment secrets are handled later by `/devops` via platform dashboards.
