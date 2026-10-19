# /draft — Viết bản nháp (giai đoạn 2, không có gate người duyệt)

Ngữ cảnh: $ARGUMENTS

1. Đọc `context/active.md` để lấy thư mục việc. Đọc `brief.md` đã được chủ duyệt (và góp ý của chủ nếu tin mở phiên có), rồi `style.md`.
2. Viết `content/<slug>/draft.md`:
   - dòng đầu là tiêu đề `# …`;
   - đủ các phần của dàn ý, đúng thứ tự (đổi thứ tự thì ghi lý do vào `context/active.md`);
   - độ dài trong khoảng 60–160% số từ của brief;
   - dữ kiện kiểm được thì kiểm (WebSearch/WebFetch), ghi mục `## Nguồn` cuối bài nếu có dùng.
3. Viết liền một mạch theo dàn ý. Chưa trau chuốt câu chữ — đó là việc của `/edit`.
4. Chạy `scripts/lazy-gate.sh draft` tới khi qua. Cập nhật `context/active.md`, rồi `handoff` + `stage_done` (số từ, phần nào còn yếu).
