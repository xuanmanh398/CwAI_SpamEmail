# 🚀 EmailFlow Tester - Tự Động Gửi Email Thử Nghiệm Phân Loại

Bộ công cụ phần mềm chuyên dụng hỗ trợ kiểm thử khả năng phân loại, định tuyến và lọc email tự động của hệ thống **EmailFlow**.

---

## 🌟 Tính Năng Nổi Bật

- **Đa Dạng Danh Mục Phân Loại (7 Category Presets)**:
  - `SPAM`: Quảng cáo, khuyến mãi bùng nổ, lừa đảo trúng thưởng.
  - `PHISHING`: Cảnh báo giả mạo tài khoản, khôi phục mật khẩu, xác thực KYC.
  - `WORK`: Email họp dự án, báo cáo sprint, phân công công việc.
  - `FINANCE`: Hóa đơn dịch vụ, xác nhận chuyển khoản, nhắc gia hạn.
  - `SUPPORT`: Yêu cầu hỗ trợ kỹ thuật (Ticket), báo lỗi hệ thống.
  - `NEWSLETTER`: Bản tin công nghệ, cập nhật hàng tuần.
  - `URGENT`: Cảnh báo sự cố khẩn cấp, bảo trì server.
- **Tự Động Sinh Nội Dung Biến Thể (AI/Template Randomizer)**: Tạo ngẫu nhiên tiêu đề, người gửi, Message-ID và nội dung HTML/Text sinh động.
- **Giao Diện Web (Streamlit Web Dashboard)**:
  - Bảng điều khiển trực quan, chọn phân loại, tùy chỉnh số lượng email và độ trễ.
  - Metrics thống kê theo thời gian thực (Sent, Success, Failed).
  - Trình xem trước mẫu email (Template Inspector).
- **Chế Độ Gửi & Kiểm Thử Linh Hoạt**:
  - Gửi qua máy chủ SMTP (Gmail, Outlook, Mailtrap Sandbox, Local SMTP).
  - **Chế độ Giả lập (Dry Run)**: Test thử nghiệm không tốn băng thông và không cần SMTP Server.
  - **Xuất tệp .EML**: Xuất email thành các file `.eml` phục vụ test import cục bộ.
- **Giao Diện Dòng Lệnh (CLI)**: Dễ dàng tích hợp vào script tự động hóa CI/CD.

---

## 🛠️ Hướng Dẫn Cài Đặt & Khởi Chạy

### ⚡ Cách Nhanh Nhất (Windows):
Chỉ cần nhấp đôi chuột vào tệp **[run.bat](file:///e:/CwAI/CwAI_SpamEmail/run.bat)** để mở menu lựa chọn khởi chạy tự động (Giao diện Web, CLI, hoặc Chạy test nhanh).

---

### 1. Khởi Chạy Giao Diện Web Trực Tiếp (Streamlit Web Dashboard)

Mở terminal tại thư mục dự án và chạy lệnh:

```bash
streamlit run app.py
```

Giao diện ứng dụng sẽ tự động bật tại địa chỉ `http://localhost:8501`.

---

### 2. Khởi Chạy Bằng Giao Diện Dòng Lệnh (CLI)

#### a) Chế độ Tương tác (Interactive Menu):
```bash
python cli.py
```

#### b) Chế độ Truyền Tham Số (CLI Flags):
```bash
# Gửi 20 email giả lập (Dry Run) đa phân loại đến email target
python cli.py --target classifier@emailflow.internal --count 20 --dry-run

# Gửi 10 email Spam qua Gmail
python cli.py --target mytarget@example.com --count 10 --category SPAM --username myemail@gmail.com --password "xxxx-xxxx-xxxx-xxxx"

# Xuất 15 email ra các file .eml
python cli.py --target test@emailflow.internal --count 15 --export-eml
```

---

## ⚙️ Cấu Hình Kết Nối SMTP

- **Gmail**: Dùng server `smtp.gmail.com:587`, bật TLS. *Lưu ý*: Cần dùng **Mật khẩu ứng dụng (App Password)** 16 ký tự.
- **Mailtrap (Tốt nhất cho testing)**: Dùng `sandbox.smtp.mailtrap.io:2525` để bắt giữ tất cả email an toàn.
- **Dry Run**: Không cần kết nối mạng.

---

## 📁 Cấu Trúc Dự Án

```
CwAI_SpamEmail/
├── app.py              # Giao diện Web Dashboard (Streamlit)
├── cli.py              # Công cụ dòng lệnh CLI & Menu tương tác
├── config.py           # Cấu hình SMTP & Presets
├── email_generator.py  # Động cơ sinh email mẫu đa danh mục & biến thể
├── email_sender.py     # Động cơ gửi SMTP & Xuất file EML
├── requirements.txt    # Danh sách thư viện phụ thuộc
└── README.md           # Hướng dẫn sử dụng chi tiết
```
