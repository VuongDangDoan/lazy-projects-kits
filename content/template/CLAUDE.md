<!-- LAZY-FACTORY-MODE: bộ content — scripts/lazy-init.sh điền tên, mục tiêu, ngôn ngữ lúc lập dự án -->
# {{DISPLAY_NAME}} — dự án nội dung (bộ content@{{KIT_VERSION}})

> **Mục tiêu:** {{DESCRIPTION}}
> **Ngôn ngữ viết:** {{LANGUAGE}}

## 0. Chạy trong Lazy Bot factory — đọc trước

- Mỗi việc (task) chạy trong một worktree riêng của repo này, **một giai đoạn mỗi phiên**. Chủ duyệt gate trên Telegram.
- **Không** `git commit`, `git push`, mở PR — factory làm việc đó.
- Không có người ở terminal:
  - cần chủ quyết định (độc giả, giọng, điều không được nói) ⇒ công cụ MCP `ask_human`, gom mọi câu hỏi vào một lần;
  - xong giai đoạn ⇒ `handoff` rồi `stage_done`. Factory chạy gate rồi hỏi chủ. **Không tự sang giai đoạn sau.**
- Không sửa `.claude/` và `.lazy/`.
- Tin mở phiên có góp ý của chủ ⇒ sửa đúng giai đoạn đó, giữ phần đã ổn.

## 1. Quy trình

| Giai đoạn | Lệnh | Kết quả | Gate |
|---|---|---|---|
| brief | `/brief` | `content/<slug>/brief.md` | `scripts/lazy-gate.sh brief` → chủ duyệt **G1** |
| draft | `/draft` | `content/<slug>/draft.md` | `scripts/lazy-gate.sh draft` |
| edit | `/edit` | `content/<slug>/final.md` + `review.md` | `scripts/lazy-gate.sh edit` → chủ duyệt **G2** |

- Mỗi việc một thư mục `content/<slug>/`, tạo bằng `scripts/new-item.sh <slug>`. Không cấp mã số, nên nhiều máy cùng repo không trùng.
- Thư mục của việc đang làm ghi trong `context/active.md` (dòng `Thư mục: content/<slug>`). Gate đọc dòng này.
- `content/_index.md`: mỗi việc một dòng (trạng thái + câu tóm tắt).
- `style.md`: giọng văn và quy ước chung của dự án. Đọc trước khi viết; chủ duyệt thêm quy ước nào thì ghi vào đây.

## 2. Luật viết

1. Viết cho độc giả trong brief, không viết cho chính mình. Mỗi đoạn phục vụ một thông điệp chính hoặc mục tiêu.
2. Khẳng định có số liệu hoặc sự thật kiểm được ⇒ kiểm bằng WebSearch/WebFetch, ghi nguồn cuối bài. Không bịa số liệu, trích dẫn, tên người.
3. Câu ngắn, chủ động, từ cụ thể. Bỏ sáo ngữ, câu rào đón, liệt kê ba thứ cho có.
4. Không nói quá về sản phẩm / dịch vụ. Điều chưa chắc ⇒ hỏi chủ (`ask_human`) hoặc bỏ.
5. Giữ tên các mục `##` của `brief.md` và `review.md` như mẫu trong `templates/`, vì gate kiểm các mục đó. Viết tiếng Anh thì dùng tên tiếng Anh ghi trong mẫu.

## 3. File

- `context/active.md` — việc đang làm + ghi chú cho phiên sau. Cập nhật trước mỗi `stage_done`.
- `templates/` — mẫu `brief.md`, `review.md`.
- `scripts/new-item.sh <slug>` — tạo thư mục việc từ mẫu, ghi `context/active.md`, thêm dòng chỉ mục.
- `scripts/lazy-gate.sh <brief|draft|edit|check>` — gate (không mạng, chỉ đọc). Chạy thử trước khi `stage_done`.
