# /scope — Chốt phạm vi nghiên cứu (giai đoạn 1, dừng ở G1)

Yêu cầu của chủ: $ARGUMENTS

1. Đọc `CLAUDE.md`, `context/active.md`, `research/_index.md`. Có việc cũ liên quan thì đọc báo cáo đó để tái dùng nguồn.
2. Đặt slug ngắn cho việc (chữ thường không dấu, số, gạch ngang, ≤ 40 ký tự, vd. `postgres-managed-gia-re`). Chạy `scripts/new-item.sh <slug>`. Script in ra thư mục thật (thêm `-2`… nếu slug đã có ở nhánh này hay nhánh khác).
3. Điền `research/<slug>/brief.md` theo mẫu. Thay mọi dòng `<!-- … -->` bằng nội dung thật:
   - **Câu hỏi** — câu hỏi chính, và các câu hỏi phụ cần trả lời để chủ ra quyết định;
   - **Phạm vi** — trong / ngoài phạm vi, giả định (ngân sách, quy mô, khu vực, thời hạn…);
   - **Tiêu chí** — mỗi tiêu chí một dòng: đo bằng gì, trọng số nếu có;
   - **Ứng viên** — các lựa chọn sẽ xét, nếu là so sánh (tra web nhanh để chọn cho đúng, chưa thu thập chi tiết);
   - **Nguồn dự kiến** — loại nguồn sẽ tra (tài liệu chính thức, bảng giá, benchmark, đánh giá người dùng…);
   - **Đầu ra** — báo cáo trả lời gì, cho quyết định nào.
4. Thiếu điều chỉ chủ biết (ngân sách, ràng buộc bắt buộc) ⇒ `ask_human` một lần, gom mọi câu hỏi. Điều suy ra được thì ghi thành giả định trong Phạm vi.
5. Chạy `scripts/lazy-gate.sh scope` tới khi qua. Cập nhật `context/active.md` (giai đoạn scope xong, điều cần nhớ).
6. Dừng ở G1: `handoff` rồi `stage_done`. Tóm tắt: thư mục, câu hỏi chính, tiêu chí, ứng viên.
