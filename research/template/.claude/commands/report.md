# /report — Viết báo cáo (giai đoạn 3, dừng ở G2)

Ngữ cảnh: $ARGUMENTS

1. Đọc `context/active.md`, rồi `brief.md` và `sources.md` của việc.
2. Chép `templates/report.md` vào thư mục việc nếu chưa có, rồi viết:
   - **Tóm tắt** (≤ 5 dòng) — câu trả lời cho câu hỏi chính + khuyến nghị;
   - **Phân tích** — theo đúng tiêu chí của brief (so sánh thì dùng bảng); mỗi số liệu / khẳng định có `[n]`;
   - **Khuyến nghị** — chọn gì, vì sao, khi nào nên chọn khác, rủi ro;
   - **Hạn chế** — khoảng trống, giả định, độ tin cậy;
   - **Nguồn** — các `[n]` đã trích, khớp `sources.md`.
3. Chỉ trích `[n]` có trong `sources.md`. Một ý quan trọng chưa có nguồn ⇒ tra thêm và ghi vào `sources.md` (số tiếp theo), hoặc ghi rõ "chưa xác minh".
4. Sửa dòng của việc trong `research/_index.md`: trạng thái "báo cáo — chờ G2", kết luận một câu.
5. Chạy `scripts/lazy-gate.sh report` tới khi qua. Cập nhật `context/active.md`.
6. Giai đoạn cuối: `propose_delivery` (tiêu đề PR "Nghiên cứu: …", mô tả = tóm tắt + đường dẫn ba file), rồi `handoff` + `stage_done`.
