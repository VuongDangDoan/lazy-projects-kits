# Hướng dẫn bắt đầu — SDLC AI Workspace
> Dành cho người dùng không có kiến thức kỹ thuật.
> Đọc từ đầu đến cuối trước khi làm bất cứ điều gì.

---

## Workspace này là gì?

Đây là một "đội ngũ AI" chuyên xây dựng phần mềm. Bạn mô tả hệ thống muốn xây bằng tiếng Việt thường ngày, AI sẽ phân tích yêu cầu, thiết kế hệ thống, viết code, tự kiểm tra và tự sửa lỗi cho bạn.

**Bạn không cần biết lập trình.** Bạn chỉ cần:
- Biết mình muốn xây gì
- Có khả năng đọc và phê duyệt kết quả (AI sẽ giải thích bằng tiếng Việt)
- Có tài khoản GitHub và một nơi để chạy hệ thống (hướng dẫn bên dưới)

**Điều quan trọng nhất cần nhớ:** AI làm việc theo 5 giai đoạn, và sẽ **dừng lại xin ý kiến bạn tại 5 cổng kiểm duyệt (G1–G5)**. Giữa các cổng, AI tự làm việc — bạn chỉ cần trả lời khi AI hỏi.

---

## Bước 1: Cài đặt công cụ (chỉ làm 1 lần)

### 1.1 Cài Claude Code

Claude Code là công cụ AI bạn sẽ dùng để trao đổi. Tải về tại:

```
https://claude.ai/download
```

Cài đặt như ứng dụng thông thường trên Mac hoặc Windows.
Sau khi cài xong, mở ứng dụng và đăng nhập bằng tài khoản Anthropic.

> Chi phí: khoảng $20/tháng (gói Claude Pro hoặc Max) — *giá tham khảo, kiểm tra giá hiện tại tại claude.ai*

### 1.2 Tạo tài khoản GitHub (miễn phí)

GitHub là nơi lưu code của bạn.

1. Vào `github.com`
2. Click "Sign up" → đăng ký bằng email
3. Chọn gói **Free** (miễn phí, đủ dùng)

> **Lưu ý bảo mật:** khi cần kết nối GitHub, AI sẽ hướng dẫn bạn chạy lệnh `gh auth login` trong terminal **của bạn**. Bạn **không bao giờ** cần dán mật khẩu hay token vào ô chat.

### 1.3 Chuẩn bị nơi chạy hệ thống (deploy)

Hệ thống của bạn cần một nơi để chạy trên internet. Với người mới bắt đầu, chúng tôi khuyến nghị **Railway**:

1. Vào `railway.app`
2. Click "Login" → đăng nhập bằng tài khoản GitHub vừa tạo
3. Không cần làm gì thêm — AI sẽ hướng dẫn cụ thể khi đến bước deploy

> Chi phí: khoảng $5/tháng khi hệ thống đang chạy — *giá tham khảo, kiểm tra giá hiện tại tại railway.app*

**Có lựa chọn khác không?** Có. Lệnh `/devops` hỗ trợ 4 phương án deploy (GitHub Actions + Railway, GitLab CI + Railway, Vercel, hoặc máy chủ riêng chạy Docker). Người mới cứ dùng Railway — đổi phương án sau bất cứ lúc nào bằng cách chạy lại `/devops`.

---

## Bước 2: Tải workspace này về máy

Trong Claude Code (ứng dụng vừa cài), mở terminal tích hợp và chạy:

```bash
git clone https://github.com/<TÊN-TỔ-CHỨC-CỦA-BẠN>/<TÊN-WORKSPACE>.git
cd <TÊN-WORKSPACE>
```

> ⚠️ `<TÊN-TỔ-CHỨC-CỦA-BẠN>` và `<TÊN-WORKSPACE>` là **chỗ cần thay** — thay bằng đường dẫn thật của repo workspace mà đội bạn cung cấp (hỏi người đưa link cho bạn).

> **Nếu bạn không biết git:** Bấm nút "Code" màu xanh trên trang GitHub của repo, chọn "Download ZIP", giải nén ra Desktop.

Sau đó mở folder workspace bằng Claude Code (File → Open Folder).

---

## Bước 3: Thiết lập dự án của bạn

Trong Claude Code, gõ lệnh sau vào ô chat:

```
/quickstart
```

AI sẽ hỏi trước **1 câu về ngôn ngữ**:
- Bạn muốn trao đổi bằng Tiếng Việt hay English?

Sau đó là **3 câu hỏi đơn giản**:
1. Hệ thống của bạn làm gì?
2. Ai sẽ dùng? (nhân viên nội bộ / khách hàng bên ngoài / cả hai)
3. Tên hệ thống là gì?

Trả lời bằng tiếng Việt thường ngày. AI sẽ tự chọn công nghệ và xử lý toàn bộ phần kỹ thuật.

**Ví dụ:**

```
1. Quản lý nhân sự cho công ty 50 người: chấm công, nghỉ phép, bảng lương
2. Nhân viên nội bộ
3. HRM Pro
```

> AI có sẵn 3 bộ mẫu ngành: **quản lý nhân sự (hrm)**, **bán hàng tại quầy (pos)**, và **bán hàng online (ecommerce)**. Nếu hệ thống của bạn thuộc một trong 3 nhóm này, AI sẽ tự nhận ra và dựng sẵn khung dữ liệu phù hợp.

---

## Bước 4: Mô tả tính năng đầu tiên

Sau khi setup xong, gõ:

```
/build "Đăng nhập và phân quyền người dùng — admin, quản lý, nhân viên"
```

> **Tại sao bắt đầu bằng đăng nhập?**
> Đây là nền tảng bảo mật — phải có trước mọi tính năng khác.
> AI sẽ tự xây hệ thống phân quyền (RBAC) an toàn, bảo vệ dữ liệu theo từng người dùng.

Sau đó thêm tính năng nghiệp vụ:

```
/build "Quản lý nhân viên — thêm, sửa, xem danh sách"
/build "Chấm công — check-in, check-out, báo cáo tháng"
/build "Đơn nghỉ phép — tạo đơn, phê duyệt, theo dõi số ngày còn lại"
```

---

## Bước 5: Xem tiến độ

Bất cứ lúc nào, gõ để xem tình trạng dự án:

```
/status
```

AI sẽ cho biết: đang ở giai đoạn nào, cổng nào đang chờ bạn duyệt, và lệnh tiếp theo nên chạy.

---

## Quy trình mỗi tính năng — 5 giai đoạn, 5 cổng duyệt

AI làm việc theo 5 giai đoạn. Tại cuối mỗi giai đoạn có một **cổng (G1–G5)** — AI dừng lại, giải thích bằng tiếng Việt, và chờ bạn duyệt. Giữa các cổng, AI tự làm việc liên tục.

```
Giai đoạn 1 — Phân tích:   "Tôi hiểu yêu cầu như thế này... Đúng không?"
                            (kèm bản phác thảo màn hình nếu có giao diện)
                            → CỔNG G1: bạn xác nhận hoặc sửa

Giai đoạn 2 — Thiết kế:    "Dữ liệu sẽ lưu những gì, API sẽ có những gì..."
                            → CỔNG G2: bạn xác nhận hoặc sửa

Giai đoạn 3 — Lập kế hoạch: "Tôi sẽ chia thành N công việc như này..."
                            → CỔNG G3: bạn xác nhận

Giai đoạn 4 — Viết code:    AI viết code, TỰ KIỂM TRA, TỰ TÌM LỖI, TỰ SỬA
                            (lặp lại đến khi sạch lỗi — bạn không cần can thiệp)
                            → CỔNG G4: AI báo cáo 1 LẦN DUY NHẤT, bạn duyệt

Giai đoạn 5 — Kiểm thử thật: AI chạy thử trên hệ thống thật như một người dùng
                            → CỔNG G5: đạt → tính năng hoàn thành
```

- Lệnh `/build` lo giúp bạn **3 giai đoạn đầu** (G1 → G2 → G3).
- Ở **giai đoạn 4**, AI tự review và tự sửa lỗi bên trong — bạn chỉ được hỏi **1 lần cuối cùng (G4)**. Không cần chạy lệnh kiểm tra riêng như trước.
- Nếu AI phát hiện **yêu cầu ban đầu có vấn đề** (chứ không phải lỗi code), nó sẽ dừng ngay và hỏi bạn — vì thay đổi yêu cầu là quyền của bạn, không phải của AI.
- Sau mỗi cổng, AI luôn báo rõ lệnh tiếp theo cần gõ (ví dụ `/dev TICKET-001`).

---

## Câu hỏi thường gặp

**Hỏi: Tôi phải tự viết code không?**
Không. AI viết toàn bộ code. Bạn chỉ đọc tóm tắt tiếng Việt và xác nhận tại các cổng.

**Hỏi: Nếu tôi muốn thay đổi yêu cầu thì sao?**
Mô tả thay đổi bình thường: "Tôi muốn thêm trường số điện thoại vào form nhân viên".

**Hỏi: Nếu có lỗi thì AI có tự sửa không?**
Có. Trong giai đoạn 4, AI tự kiểm tra và tự sửa lỗi code (tối đa 3 vòng) trước khi báo cáo cho bạn. Nếu sau đó bạn phát hiện lỗi khi dùng thử, chỉ cần mô tả lỗi — AI sẽ xử lý theo quy trình sửa lỗi.

**Hỏi: AI có bao giờ tự ý làm quá đà không?**
Không. AI không bao giờ vượt qua một cổng (G1–G5) khi chưa có sự đồng ý của bạn, và không bao giờ tự ý đưa code lên GitHub — bước đó luôn do bạn thực hiện (AI soạn sẵn nội dung, bạn bấm xác nhận trong terminal của mình).

**Hỏi: Tôi có bao giờ phải đưa mật khẩu cho AI không?**
**Không bao giờ.** Đừng dán mật khẩu, token, hay khóa bí mật vào ô chat. Khi cần kết nối tài khoản (GitHub, nơi deploy...), AI sẽ đưa hướng dẫn để **bạn tự chạy lệnh trong terminal của mình** hoặc tự nhập trong trang quản trị của dịch vụ.

**Hỏi: Code có an toàn không?**
Có. Mọi dự án đều tự động có:
- Bảo vệ SQL Injection (không bao giờ dùng raw SQL)
- Bảo vệ XSS (framework tự escape)
- Phiên đăng nhập an toàn (httpOnly cookies)
- Rate limiting trên endpoint nhạy cảm
- Phân quyền theo vai trò (RBAC)
- Mỗi lần viết code, AI đều chạy một vòng kiểm tra bảo mật riêng

**Hỏi: Hệ thống sẽ chạy ở đâu?**
Mặc định là Railway — tự động deploy mỗi khi code được đưa lên GitHub. Muốn dùng nơi khác (Vercel, GitLab, máy chủ riêng), chạy `/devops` và chọn 1 trong 4 phương án. Hệ thống luôn tự kiểm tra code đạt chuẩn **trước khi** deploy.

---

## Chi phí tổng hợp

> ⚠️ Các con số dưới đây chỉ mang tính **tham khảo** tại thời điểm viết — hãy kiểm tra giá hiện tại trên trang của từng dịch vụ.

| Dịch vụ | Gói | Giá tham khảo |
|---|---|---|
| Claude Code | Pro / Max | ~$20/tháng |
| GitHub | Free | Miễn phí |
| Railway | Starter | ~$5/tháng |
| Cloudflare | Free | Miễn phí |
| **Tổng** | | **~$25/tháng** |

> Cloudflare (tùy chọn, khuyến nghị): thêm lớp bảo vệ DDoS miễn phí, trỏ domain về nơi deploy.

---

## Cần hỗ trợ?

Mô tả vấn đề trực tiếp trong Claude Code — AI sẽ giúp bạn giải quyết. Gõ `/status` bất cứ lúc nào nếu bạn không chắc mình đang ở bước nào.
