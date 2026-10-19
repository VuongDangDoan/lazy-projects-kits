<!-- LAZY-FACTORY-MODE: bộ research — scripts/lazy-init.sh điền tên, mục tiêu, ngôn ngữ lúc lập dự án -->
# {{DISPLAY_NAME}} — dự án nghiên cứu (bộ research@{{KIT_VERSION}})

> **Mục tiêu:** {{DESCRIPTION}}
> **Ngôn ngữ viết:** {{LANGUAGE}}

## 0. Chạy trong Lazy Bot factory — đọc trước

- Mỗi việc (task) chạy trong một worktree riêng của repo này, **một giai đoạn mỗi phiên**. Chủ duyệt gate trên Telegram.
- **Không** `git commit`, `git push`, mở PR — factory làm việc đó.
- Không có người ở terminal:
  - cần chủ quyết định (ngân sách, ràng buộc chỉ chủ biết) ⇒ công cụ MCP `ask_human`, gom mọi câu hỏi vào một lần;
  - xong giai đoạn ⇒ `handoff` rồi `stage_done`. Factory chạy gate rồi hỏi chủ. **Không tự sang giai đoạn sau.**
- Không sửa `.claude/` và `.lazy/`.
- Tin mở phiên có góp ý của chủ ⇒ sửa đúng giai đoạn đó, giữ phần đã ổn.

## 1. Quy trình

| Giai đoạn | Lệnh | Kết quả | Gate |
|---|---|---|---|
| scope | `/scope` | `research/<slug>/brief.md` | `scripts/lazy-gate.sh scope` → chủ duyệt **G1** |
| research | `/research` | `research/<slug>/sources.md` | `scripts/lazy-gate.sh research` |
| report | `/report` | `research/<slug>/report.md` | `scripts/lazy-gate.sh report` → chủ duyệt **G2** |

- Mỗi việc một thư mục `research/<slug>/`, tạo bằng `scripts/new-item.sh <slug>`. Không cấp mã số, nên nhiều máy cùng repo không trùng.
- Thư mục của việc đang làm ghi trong `context/active.md` (dòng `Thư mục: research/<slug>`). Gate đọc dòng này.
- `research/_index.md`: mỗi việc một dòng (trạng thái + kết luận một câu).

## 2. Luật nghiên cứu

1. Mỗi khẳng định quan trọng có nguồn `[n]` trong `sources.md`. Số liệu (giá, giới hạn, phiên bản) ghi ngày truy cập.
2. Ưu tiên nguồn gốc: tài liệu chính thức, bảng giá, changelog, paper, mã nguồn. Bài tổng hợp chỉ là nguồn phụ, ghi rõ.
3. **Không bịa** nguồn, link hay số liệu. Không tìm được ⇒ ghi "chưa xác minh" và nói rõ trong báo cáo.
4. Tách sự thật (có nguồn) với nhận định của bạn ("Nhận định:").
5. Tra bằng WebSearch, rồi WebFetch trang gốc trước khi trích. Không trích từ đoạn tóm tắt của kết quả tìm kiếm.
6. Trung lập: nêu cả điểm yếu của phương án được khuyến nghị, và khi nào nên chọn khác.
7. Giữ tên các mục `##` như mẫu trong `templates/`, vì gate kiểm các mục đó. Viết tiếng Anh thì dùng tên tiếng Anh ghi trong mẫu.

## 3. File

- `context/active.md` — việc đang làm + ghi chú cho phiên sau. Cập nhật trước mỗi `stage_done`.
- `templates/` — mẫu `brief.md`, `sources.md`, `report.md`.
- `scripts/new-item.sh <slug>` — tạo thư mục việc từ mẫu, ghi `context/active.md`, thêm dòng chỉ mục.
- `scripts/lazy-gate.sh <scope|research|report|check>` — gate (không mạng, chỉ đọc). Chạy thử trước khi `stage_done`.
