# lazy-kits — các bộ workspace cho Lazy Bot factory

Mỗi thư mục là một **bộ** (kit): quy trình + "nhân sự" agent mà Claude Code tự nạp khi làm việc
trong dự án (CLAUDE.md, `.claude/commands`, `.agents/` roles, contracts, scripts, templates).
Factory **không** biên dịch hay ghép các file này — nó chỉ chép bộ vào repo dự án mới, chạy
onboard, rồi cho agent chạy với `--setting-sources project` (ADR-012 trong agents-workspace).

## Các bộ

| Bộ | Dùng khi (`use_when`) | Giai đoạn |
|---|---|---|
| `sdlc` | Đầu ra là phần mềm chạy được (app, API, công cụ, tính năng có code) | ba (G1) → sa (G2) → planner (G3) → build (G4) |
| `research` | Tìm hiểu, so sánh, đánh giá, khảo sát; đầu ra là báo cáo có nguồn + khuyến nghị | scope (G1) → research → report (G2) |
| `content` | Đầu ra là chữ để người đọc: blog, giới thiệu sản phẩm, tài liệu, kịch bản, email | brief (G1) → draft → edit (G2) |

LAZY không có bộ mặc định: khi lập team, nó so việc của chủ với `description` / `use_when` / giai đoạn của
từng bộ rồi chọn, và ghi lý do trên thẻ 🏗️. Thêm bộ mới = thêm thư mục ở đây với `use_when` rõ ràng.

```
lazy-kits/
├── README.md
├── research/             ← nghiên cứu → báo cáo có nguồn (bộ gọn: CLAUDE.md, 3 lệnh, gate Python)
├── content/              ← viết nội dung → bản cuối đã biên tập (bộ gọn)
└── sdlc/                 ← bộ phát triển phần mềm (BA → SA → Planner → Build, G1–G4)
    ├── kit.yaml          ← tên, version, init, test_command, các giai đoạn (lệnh + gate)
    └── template/         ← chép nguyên vào gốc repo dự án
        ├── .claude/commands/   /ba /sa /planner /dev /factory-build …
        ├── .agents/            roles + contracts + orchestration
        ├── scripts/            scaffold, validators, lazy-init.sh, lazy-gate.sh
        ├── templates/          scaffold (CLAUDE.md, AGENTS.md, knowledge…), lazy/factory-mode.md
        └── knowledge/stacks/   pattern theo stack
```

## kit.yaml

| Khoá | Ý nghĩa |
|---|---|
| `name`, `version`, `description` | hiện ở `factory kit list` và thẻ "Lập team" |
| `use_when` | tuỳ chọn — khi nào dùng bộ (và khi nào không); LAZY so việc với đoạn này để chọn bộ |
| `init` | script chạy trong bản chép (không credential, không mạng) để onboard từ `.lazy/project.json` |
| `test_command` | lệnh test mặc định của dự án (gate) |
| `stages[]` | `id`, `goal`, `command` (lệnh của bộ; `{request}` = yêu cầu của chủ), `gate.script`, `gate.human` (nhãn G1… — factory hỏi chủ duyệt trên Telegram), `gate.timeout_s`, `gate.max_retries` |

Bản `kit.yaml` được chép vào repo dự án thành `.lazy/kit.yaml`: muốn đổi quy trình của **một** dự án,
sửa file đó bằng PR trong repo dự án; muốn đổi cho các dự án **mới**, sửa bộ ở đây.

## Bộ gọn (research, content)

- Mỗi việc một thư mục `<research|content>/<slug>/`, tạo bằng `scripts/new-item.sh <slug>`. Script tránh slug đã có ở nhánh này hay nhánh `origin/*` khác, nên không cần cấp mã.
- `context/active.md` ghi thư mục việc đang làm (gate đọc), gộp `merge=ours`. Chỉ mục `_index.md` gộp `merge=union`.
- `scripts/lazy-gate.sh <giai đoạn>|check` gọi `scripts/kit_check.py`: chỉ đọc file, không mạng.
  - Kiểm các mục `##` bắt buộc đã có nội dung thật (không chỉ chú thích của mẫu).
  - research: ≥ 3 nguồn có link; báo cáo trích `[n]` có trong `sources.md`.
  - content: bài có tiêu đề, độ dài 60–160% số từ của brief, checklist biên tập không còn `[ ]`.
- `scripts/lazy-init.sh` điền tên / mục tiêu / ngôn ngữ từ `.lazy/project.json` vào CLAUDE.md, README (+ `style.md`).
- Kiểm hai bộ: `tests/lean-kits.sh` (chép bộ ra thư mục tạm, chạy init, new-item, mọi gate cả đường trượt lẫn đường qua).

## Phiên bản

Factory ghim commit của repo này lúc lập dự án (hiện kèm `version` trong kit.yaml). Tăng `version`
mỗi khi đổi bộ; dự án cũ không tự đổi.

- **2026-10-17 — chọn bộ theo loại việc:** thêm `research` 0.1.0 và `content` 0.1.0; `sdlc` 0.3.2 chỉ thêm `use_when`.
- **sdlc 0.3.1** (2026-10-17): nhiều factory cùng một repo (ADR-014 của Lazy Bot).
  - `scripts/next-id.sh` xét cả mã đã có trên các nhánh `origin/*`, gồm nhánh task factory khác đã đẩy.
  - `.gitattributes` gộp file chỉ mục kiểu union; `active-context.md` giữ bản của nhánh.
  - Dự án lập từ 0.3.0: chép hai file này vào repo dự án bằng một PR.

## Nguồn của bộ sdlc

Khung của `agents-workspace` (Lazy Bot, 2026-10-17), bỏ toàn bộ dữ liệu dự án; thêm chế độ factory:
`scripts/lazy-init.sh` (+ `lazy_init.py`), `scripts/lazy-gate.sh`, `templates/lazy/factory-mode.md`,
`.claude/commands/factory-build.md`; `.gitignore` không bỏ qua `_source/` (code nằm trong repo dự án).
