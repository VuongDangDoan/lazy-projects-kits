# /brief — Chốt brief nội dung (giai đoạn 1, dừng ở G1)

Yêu cầu của chủ: $ARGUMENTS

1. Đọc `CLAUDE.md`, `style.md`, `context/active.md`, `content/_index.md`. Có bài cũ cùng chủ đề thì đọc để không lặp ý.
2. Đặt slug ngắn cho việc (chữ thường không dấu, số, gạch ngang, ≤ 40 ký tự, vd. `gioi-thieu-lazy-bot`). Chạy `scripts/new-item.sh <slug>`. Script in ra thư mục thật (thêm `-2`… nếu slug đã có).
3. Điền `content/<slug>/brief.md` theo mẫu. Thay mọi dòng `<!-- … -->` bằng nội dung thật:
   - **Độc giả** — ai đọc, họ biết gì sẵn, họ cần gì;
   - **Mục tiêu** — sau khi đọc, độc giả hiểu / làm gì;
   - **Kênh** — đăng ở đâu (blog, docs, LinkedIn, email…), định dạng;
   - **Giọng văn** — vd. thân thiện, kỹ thuật vừa phải, xưng hô;
   - **Thông điệp chính** — 2–4 ý phải đọng lại;
   - **Dàn ý** — tiêu đề dự kiến + các phần, mỗi phần một dòng nói ý chính;
   - **Độ dài** — số từ mục tiêu (vd. "khoảng 800 từ");
   - **Nguồn / dữ kiện** — dữ kiện cần dùng và chỗ lấy (repo, tài liệu, web).
4. Thiếu điều chỉ chủ biết ⇒ `ask_human` một lần, gom mọi câu hỏi. Điều suy ra được thì ghi thành giả định.
5. Chạy `scripts/lazy-gate.sh brief` tới khi qua. Cập nhật `context/active.md`.
6. Dừng ở G1: `handoff` rồi `stage_done`. Tóm tắt: thư mục, độc giả, thông điệp chính, dàn ý.
