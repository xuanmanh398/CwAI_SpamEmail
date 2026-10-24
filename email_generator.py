import random
import time
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any

@dataclass
class GeneratedEmail:
    id: str
    category: str
    subject: str
    sender_name: str
    body_text: str
    body_html: str
    priority: str = "normal"  # low, normal, high, urgent
    headers: Dict[str, str] = field(default_factory=dict)
    has_attachment_hint: bool = False

# Mẫu Email theo từng phân loại (Category Templates)
EMAIL_CATEGORIES = {
    "SPAM": {
        "label": "Quảng cáo / Spam",
        "description": "Các email khuyến mãi, trúng thưởng, mời mua hàng, crypto lừa đảo.",
        "subjects": [
            "🔥 Bùng nổ ưu đãi: Giảm ngay 70% tất cả sản phẩm hôm nay!",
            "🎉 Chúc mừng! Bạn đã trúng thưởng iPhone 16 Pro Max",
            "💰 Cơ hội đầu tư Crypto x100 tài sản trong 24 giờ",
            "⚡ Mua 1 tặng 1 - Chương trình tri ân khách hàng đặc biệt",
            "🚨 Nhận ngay voucher 500k khi truy cập liên kết này",
            "💊 Giải pháp làm đẹp cấp tốc bí truyền không thể bỏ qua"
        ],
        "senders": [
            "Khuyến Mãi Siêu Tốc <promo@fastdeals-online.com>",
            "Quỹ Đầu Tư Crypto <invest@crypto-moon-x.io>",
            "Trung Tâm Tri ân <rewards@lucky-winner-event.net>",
            "Flash Sale Hot <sales@super-discount-shop.org>"
        ],
        "bodies": [
            """Xin chào quý khách,

Chỉ duy nhất trong hôm nay! Chương trình siêu giảm giá lớn nhất năm đã bắt đầu.
- Giảm giá đến 70% toàn bộ gian hàng.
- Miễn phí vận chuyển toàn quốc.
- Nhận phần quà trị giá 2.000.000 VNĐ.

Bấm vào link ngay để nhận ưu đãi trước khi hết suất: http://bit.ly/deal-hot-2026

Trân trọng,
Đội ngũ PromoFast""",
            """THÔNG BÁO TRÚNG THƯỞNG!

Tài khoản email của bạn đã được lựa chọn ngẫu nhiên trong chương trình quay số may mắn quý 3.
Phần thưởng: 01 ĐT iPhone 16 Pro Max 256GB.

Vui lòng hoàn tất xác minh thông tin cá nhân trong vòng 24h tại: http://rewards-verify-now.com

Lưu ý: Qua 24h phần thưởng sẽ chuyển cho người tiếp theo."""
        ],
        "priority": "low"
    },
    
    "PHISHING": {
        "label": "Cảnh báo Giả mạo / Phishing",
        "description": "Các email giả mạo ngân hàng, dịch vụ mạng yêu cầu đăng nhập khẩn cấp.",
        "subjects": [
            "⚠️ CẢNH BÁO: Phát hiện truy cập bất thường vào tài khoản của bạn",
            "🔒 [Cần xử lý ngay] Tài khoản EmailFlow của bạn tạm thời bị khóa",
            "🏦 Ngân hàng VietBank: Yêu cầu cập nhật thông tin KYC bắt buộc",
            "🔑 Thay đổi mật khẩu tài khoản thành công? (Nếu không phải bạn, ấn vào đây)",
            "❌ Giao dịch $499.00 đã được thanh toán - Kiểm tra chi tiết"
        ],
        "senders": [
            "Trung Tâm Bảo Mật <security-alert@account-verify-service.com>",
            "Dịch Vụ Khách Hàng VietBank <support@vietbank-verify.net>",
            "System Administrator <admin-notice@cloud-auth-secure.org>",
            "Accounts Verification <no-reply@auth-update-center.com>"
        ],
        "bodies": [
            """Kính gửi người dùng,

Hệ thống phát hiện một lần đăng nhập từ IP lạ (Location: Moscow, Russia) vào tài khoản của bạn lúc 03:14 AM.

Nếu bạn không thực hiện giao dịch này, vui lòng XÁC MINH VÀ ĐỔI MẬT KHẨU NGAY LẬP TỨC tại đường dẫn an toàn:
https://secure-login-account-update.com/reset

Nếu không xác minh trong 12 giờ, tài khoản của bạn sẽ bị tạm khóa vĩnh viễn.

Phòng Bảo Mật Hệ Thống.""",
            """Kính chào Quý khách,

Tài khoản ngân hàng trực tuyến của Quý khách cần bổ sung xác thực sinh trắc học theo quy định mới.

Vui lòng đăng nhập cổng xác thực tại: https://ebanking-update-kyc.com để không bị gián đoạn giao dịch chuyển tiền.

Trân trọng,"""
        ],
        "priority": "urgent"
    },

    "WORK": {
        "label": "Công việc / Dự án",
        "description": "Email trao đổi nội bộ, họp hành, báo cáo tiến độ dự án.",
        "subjects": [
            "📅 [Mời họp] Thảo luận kế hoạch triển khai EmailFlow Q4",
            "📊 Báo cáo tiến độ Sprint 14 & Kế hoạch phát triển tính năng mới",
            "📝 Biên bản cuộc họp ban giám đốc ngày 28/09/2026",
            "🔄 Review thiết kế kiến trúc hệ thống xử lý Email tập trung",
            "❓ [Cần phản hồi] Yêu cầu duyệt ngân sách mua thiết bị Server"
        ],
        "senders": [
            "Nguyen Van A (PM) <a.nguyen@company.com>",
            "Tran Thi B (Lead Tech) <b.tran@company.com>",
            "Le Van C (Product Owner) <c.le@company.com>",
            "HR Department <hr@company.com>"
        ],
        "bodies": [
            """Chào cả team,

Thân mời mọi người tham gia cuộc họp rà soát tiến độ dự án EmailFlow tuần này.

- Thời gian: 14:00 - 15:00, Chiều thứ Ba
- Địa điểm: Phòng họp 302 / Google Meet Link
- Nội dung chính:
  1. Đánh giá khả năng phân loại email theo ngữ cảnh của EmailFlow.
  2. Tối ưu thuật toán lọc Spam & Router ticket tự động.
  3. Kế hoạch Release v2.0.

Mọi người chuẩn bị slide báo cáo của phần việc tương ứng nhé.

Best regards,
Nguyễn Văn A - Project Manager""",
            """Chào chị Bích,

Em đã gửi bản phác thảo thiết kế hệ thống phân loại EmailFlow trong file đính kèm. Chị xem qua và cho em xin ý kiến phản hồi trước 17h hôm nay để em kịp hoàn thiện gửi khách hàng nhé.

Cảm ơn chị!
Lê Văn C - Senior Developer"""
        ],
        "priority": "normal"
    },

    "FINANCE": {
        "label": "Tài chính / Hóa đơn",
        "description": "Hóa đơn thanh toán, xác nhận chuyển khoản, sao kê tài chính.",
        "subjects": [
            "🧾 [Hóa đơn #INV-2026-9081] Thông báo thanh toán dịch vụ Cloud Server",
            "✅ Xác nhận thanh toán thành công giao dịch #PAY-882910",
            "📄 Biên lai điện tử dịch vụ EmailFlow Enterprise - Tháng 9/2026",
            "⚠️ [Nhắc nợ] Hóa đơn gia hạn tên miền sắp hết hạn",
            "📊 Báo cáo đối soát tài chính hàng tháng - Công ty ABC"
        ],
        "senders": [
            "Phòng Kế Toán <billing@cloud-provider.com>",
            "Hệ Thống Hóa Đơn Điện Tử <invoice@einvoice-service.vn>",
            "Bộ Phận Tài Chính <finance@company.com>",
            "PayService Notification <no-reply@payservice.com>"
        ],
        "bodies": [
            """Kính gửi Quý khách hàng,

Cảm ơn Quý khách đã sử dụng dịch vụ của chúng tôi. Dưới đây là thông tin hóa đơn tháng 09/2026:

- Mã hóa đơn: INV-2026-9081
- Ngày xuất: 28/09/2026
- Số tiền: 5.500.000 VNĐ
- Trạng thái: Chưa thanh toán
- Hạn thanh toán: 05/10/2026

Quý khách vui lòng chuyển khoản theo thông tin trong file hóa đơn đính kèm.

Bộ phận Kế toán & Tài chính.""",
            """Thông báo thanh toán thành công!

Mã giao dịch: PAY-882910
Số tiền: 1.250.000 VNĐ
Nội dung: Gia hạn gói EmailFlow Professional (1 năm)
Thời gian: 28/09/2026 10:15:22

Cảm ơn bạn đã tin tưởng dịch vụ của chúng tôi!"""
        ],
        "priority": "normal"
    },

    "SUPPORT": {
        "label": "Hỗ trợ khách hàng / Ticket",
        "description": "Ticket hỗ trợ kỹ thuật, báo lỗi, phản hồi từ khách hàng.",
        "subjects": [
            "🆘 [Ticket #TCK-4401] Khách hàng báo lỗi không phân loại được email đính kèm EML",
            "💬 [Hỗ trợ kỹ thuật] Cần trợ giúp cấu hình cổng SMTP Port 587",
            "❓ Phản hồi câu hỏi về chính sách nâng cấp tài khoản EmailFlow",
            "🐛 [Bug Report] Lỗi gán sai tag 'Khẩn cấp' cho email bản tin",
            "⭐ Đánh giá trải nghiệm dịch vụ hỗ trợ EmailFlow"
        ],
        "senders": [
            "EmailFlow Customer Desk <support@emailflow-app.io>",
            "Phạm Hoàng D (Helpdesk) <helpdesk@company.com>",
            "Client Inquiry <client-contact@external-partner.com>"
        ],
        "bodies": [
            """Xin chào đội ngũ Support,

Tôi đang thử nghiệm phần mềm EmailFlow nhưng gặp sự cố khi cấu hình máy chủ SMTP. 
Hệ thống báo lỗi 'Connection Timeout' khi gửi qua cổng 587.

Thông số tôi đang dùng:
- Host: smtp.gmail.com
- Port: 587
- TLS: Enabled

Rất mong nhận được sự trợ giúp sớm từ kỹ thuật!

Trân trọng,
Khách hàng Trần Quốc E""",
            """Ticket #TCK-4401 đã được cập nhật:

Trạng thái: Đang xử lý (In Progress)
Người phụ trách: Phạm Hoàng D

Nội dung cập nhật: Chúng tôi đã tiếp nhận báo lỗi về việc phân loại file EML và đang kiểm tra lại bộ lọc AI. Sẽ phản hồi quý khách trong vòng 2 tiếng."""
        ],
        "priority": "high"
    },

    "NEWSLETTER": {
        "label": "Bản tin / Newsletter",
        "description": "Bản tin công nghệ, cập nhật thông tin hàng tuần, bài viết chuyên môn.",
        "subjects": [
            "📰 [EmailFlow Weekly] Điểm tin công nghệ AI & Email Automation tuần này",
            "💡 5 Mẹo tối ưu hóa bộ phân loại Email tự động cho doanh nghiệp",
            "🚀 Xu hướng Công nghệ 2026: AI Agent làm thay đổi Email Workflow như thế nào?",
            "📚 Bản tin kỹ thuật: Hướng dẫn tích hợp SMTP & IMAP an toàn"
        ],
        "senders": [
            "Tech Insights Newsletter <newsletter@tech-digest.io>",
            "EmailFlow Blog Team <blog@emailflow-app.io>",
            "Developer Community <updates@dev-weekly.org>"
        ],
        "bodies": [
            """Chào độc giả thân thiết,

Chào mừng bạn đến với bản tin Tech Insights tuần 39!

Trong số này có gì nổi bật?
1. 🤖 AI Agent trong xử lý Email: Thay đổi cách phân loại & tự động trả lời.
2. 🔒 Xu hướng bảo mật email năm 2026: Chống giả mạo SPF/DKIM/DMARC.
3. 🛠️ Top 5 công cụ test máy chủ SMTP tốt nhất dành cho Tester & Developer.

Đọc bài viết chi tiết tại website của chúng tôi!

Đội ngũ biên tập Tech Insights.""",
        ],
        "priority": "low"
    },

    "URGENT": {
        "label": "Thông báo Khẩn cấp",
        "description": "Các email sự cố server, thông báo khẩn từ lãnh đạo.",
        "subjects": [
            "🚨 [URGENT] Sự cố sập server Mail Primary - Cần hỗ trợ khẩn cấp!",
            "⚡ [KHẨN CẤP] Thay đổi lịch họp đột xuất với đối tác nước ngoài",
            "🔴 Cảnh báo dung lượng ổ cứng Mail Server đã đạt 98%",
            "📢 Thông báo khẩn: Bảo trì hệ thống EmailFlow toàn quốc đêm nay"
        ],
        "senders": [
            "NOC System Monitor <noc-alert@company.com>",
            "CEO Office <ceo-assistant@company.com>",
            "DevOps Team <devops-alerts@cloud.io>"
        ],
        "bodies": [
            """[THÔNG BÁO KHẨN CẤP]

Hệ thống giám sát phát hiện Server Mail Primary bị gián đoạn kết nối lúc 10:30 AM.
Tất cả các email gửi đến đang bị dồn vào Queue.

Đề nghị đội DevOps và SysAdmin vào room họp khẩn cấp để xử lý ngay lập tức!

NOC System Monitor.""",
        ],
        "priority": "urgent"
    }
}


class EmailGenerator:
    """Tạo các email giả lập chất lượng cao với biến thể phong phú phục vụ testing."""

    @staticmethod
    def generate_single_email(
        category: str,
        target_email: str,
        custom_keywords: Optional[List[str]] = None,
        index: int = 1
    ) -> GeneratedEmail:
        cat_key = category.upper()
        if cat_key not in EMAIL_CATEGORIES:
            cat_key = random.choice(list(EMAIL_CATEGORIES.keys()))

        template_data = EMAIL_CATEGORIES[cat_key]

        subject_raw = random.choice(template_data["subjects"])
        sender_raw = random.choice(template_data["senders"])
        body_raw = random.choice(template_data["bodies"])
        priority = template_data.get("priority", "normal")

        # Thêm yếu tố ngẫu nhiên để nội dung không bị lặp lại hoàn toàn (Unique content)
        random_suffix = f" [TestID-{random.randint(10000, 99999)}-#{index}]"
        subject = f"{subject_raw}{random_suffix}"

        # Nếu có custom keywords, chèn vào tiêu đề hoặc nội dung
        keyword_str = ""
        if custom_keywords:
            selected_kw = random.sample(custom_keywords, min(len(custom_keywords), 2))
            keyword_str = f"\n\n[Keywords: {', '.join(selected_kw)}]"
            subject = f"[{selected_kw[0]}] {subject}"

        body_text = f"{body_raw}\n\n---\nEmail này được tự động tạo bởi EmailFlow Tester.\nThời gian: {time.strftime('%Y-%m-%d %H:%M:%S')}\nCategory: {cat_key}{keyword_str}"

        # Tạo bản HTML sinh động
        body_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ padding: 20px; border: 1px solid #ddd; border-radius: 8px; background-color: #f9f9f9; }}
                .badge {{ display: inline-block; padding: 4px 10px; background: #007bff; color: white; border-radius: 4px; font-size: 12px; }}
                .spam {{ background: #dc3545; }}
                .phishing {{ background: #ffc107; color: #000; }}
                .work {{ background: #28a745; }}
                .urgent {{ background: #bd2130; font-weight: bold; }}
                .footer {{ margin-top: 20px; font-size: 12px; color: #777; border-top: 1px solid #eee; padding-top: 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <span class="badge {cat_key.lower()}">Phân loại: {cat_key}</span>
                <h2>{subject_raw}</h2>
                <div style="white-space: pre-line;">{body_raw}</div>
                {f'<p style="color: #666; font-style: italic;">Tags: {", ".join(custom_keywords)}</p>' if custom_keywords else ''}
                <div class="footer">
                    <p>⚡ Automated EmailFlow Stress Test | Message ID: {random.randint(100000, 999999)}</p>
                    <p>Target: {target_email} | Priority: {priority.upper()}</p>
                </div>
            </div>
        </body>
        </html>
        """

        headers = {
            "X-EmailFlow-Test": "True",
            "X-EmailFlow-Category": cat_key,
            "X-Test-Batch-ID": f"BATCH-{int(time.time())}",
            "X-Priority": "1" if priority in ["urgent", "high"] else "3"
        }

        return GeneratedEmail(
            id=f"MSG-{random.randint(100000, 999999)}",
            category=cat_key,
            subject=subject,
            sender_name=sender_raw,
            body_text=body_text,
            body_html=body_html,
            priority=priority,
            headers=headers
        )

    @classmethod
    def generate_batch(
        cls,
        count: int,
        target_email: str,
        categories: Optional[List[str]] = None,
        custom_keywords: Optional[List[str]] = None
    ) -> List[GeneratedEmail]:
        """Tạo danh sách nhiều email theo tỷ lệ phân loại mong muốn."""
        if not categories:
            categories = list(EMAIL_CATEGORIES.keys())

        emails = []
        for i in range(1, count + 1):
            cat = random.choice(categories)
            email_obj = cls.generate_single_email(
                category=cat,
                target_email=target_email,
                custom_keywords=custom_keywords,
                index=i
            )
            emails.append(email_obj)
        return emails
