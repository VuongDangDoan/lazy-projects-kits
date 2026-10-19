# /edit — Biên tập ra bản cuối (giai đoạn 3, dừng ở G2)

Ngữ cảnh: $ARGUMENTS

1. Đọc `context/active.md`, rồi `brief.md`, `draft.md` của việc và `style.md`.
2. Đọc bản nháp như độc giả trong brief. Ghi vấn đề trước, sửa sau: ý thừa, đoạn lan man, chỗ khó hiểu, giọng lệch, thông điệp chính bị chìm, tiêu đề / mở bài yếu.
3. Viết `content/<slug>/final.md` (tiêu đề `# …`, độ dài 60–160% số từ của brief). Bản nháp giữ nguyên để chủ so sánh.
4. Chép `templates/review.md` thành `content/<slug>/review.md` rồi điền:
   - **Checklist** — đánh `[x]` từng mục đã đạt; mục không áp dụng thì `[~]` kèm " — lý do". Không để `[ ]`.
   - **Thay đổi so với bản nháp** — các sửa chính và vì sao.
   - **Câu hỏi cho chủ** — điều cần chủ quyết (không có thì ghi "Không có.").
5. Sửa dòng của việc trong `content/_index.md`: trạng thái "bản cuối — chờ G2", tóm tắt một câu.
6. Chạy `scripts/lazy-gate.sh edit` tới khi qua. Cập nhật `context/active.md`.
7. Giai đoạn cuối: `propose_delivery` (tiêu đề PR "Nội dung: …", mô tả = tóm tắt + đường dẫn `final.md`), rồi `handoff` + `stage_done`.
