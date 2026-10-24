import smtplib
import time
import os
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate, make_msgid
from typing import Callable, Optional, List, Dict, Any

from config import SMTPConfig
from email_generator import GeneratedEmail

# Thiết lập logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("EmailSender")

class EmailSender:
    """Động cơ gửi Email qua SMTP hoặc Xuất file EML."""

    def __init__(self, config: SMTPConfig):
        self.config = config

    def test_connection(self) -> tuple[bool, str]:
        """Kiểm tra kết nối đến máy chủ SMTP."""
        if self.config.dry_run:
            return True, "Chế độ Giả lập (Dry Run) luôn hoạt động thành công mà không cần máy chủ SMTP."

        try:
            if self.config.use_ssl:
                server = smtplib.SMTP_SSL(self.config.smtp_server, self.config.smtp_port, timeout=10)
            else:
                server = smtplib.SMTP(self.config.smtp_server, self.config.smtp_port, timeout=10)
                if self.config.use_tls:
                    server.starttls()

            if self.config.username and self.config.password:
                server.login(self.config.username, self.config.password)
            
            server.quit()
            return True, f"Kết nối thành công đến {self.config.smtp_server}:{self.config.smtp_port}!"
        except smtplib.SMTPAuthenticationError as auth_err:
            logger.error(f"Lỗi xác thực SMTP: {str(auth_err)}")
            return False, f"❌ Lỗi Mật khẩu/Tài khoản (535 Bad Credentials): Mật khẩu ứng dụng 16 ký tự không đúng hoặc không thuộc tài khoản '{self.config.username}'. Vui lòng tạo lại Mật khẩu ứng dụng."
        except Exception as e:
            logger.error(f"Kiểm tra kết nối thất bại: {str(e)}")
            return False, f"Lỗi kết nối SMTP: {str(e)}"

    def build_mime_message(self, email_item: GeneratedEmail, target_email: str) -> MIMEMultipart:
        """Tạo đối tượng MIME Email chuẩn với đầy đủ Header và HTML/Text body."""
        msg = MIMEMultipart("alternative")
        
        # Sender Header
        effective_sender = self.config.get_effective_sender()
        if self.config.sender_name:
            msg['From'] = f"{self.config.sender_name} <{effective_sender}>"
        else:
            msg['From'] = effective_sender

        msg['To'] = target_email
        msg['Subject'] = email_item.subject
        msg['Date'] = formatdate(localtime=True)
        msg['Message-ID'] = make_msgid(domain="emailflow.test")

        # Custom headers cho EmailFlow phân loại
        for h_key, h_val in email_item.headers.items():
            msg[h_key] = h_val

        if email_item.priority == "urgent":
            msg['X-Priority'] = '1'
            msg['Importance'] = 'High'
        elif email_item.priority == "high":
            msg['X-Priority'] = '2'
            msg['Importance'] = 'High'

        # Đính kèm nội dung Text và HTML
        part_text = MIMEText(email_item.body_text, 'plain', 'utf-8')
        part_html = MIMEText(email_item.body_html, 'html', 'utf-8')

        msg.attach(part_text)
        msg.attach(part_html)

        return msg

    def send_single(self, email_item: GeneratedEmail, target_email: str) -> tuple[bool, str]:
        """Gửi một email duy nhất."""
        msg = self.build_mime_message(email_item, target_email)

        if self.config.dry_run:
            logger.info(f"[DRY-RUN] Giả lập gửi Email ID: {email_item.id} -> {target_email} | Category: {email_item.category}")
            time.sleep(0.1)
            return True, f"[DRY-RUN] Giả lập thành công email #{email_item.id}"

        try:
            if self.config.use_ssl:
                server = smtplib.SMTP_SSL(self.config.smtp_server, self.config.smtp_port, timeout=15)
            else:
                server = smtplib.SMTP(self.config.smtp_server, self.config.smtp_port, timeout=15)
                if self.config.use_tls:
                    server.starttls()

            if self.config.username and self.config.password:
                server.login(self.config.username, self.config.password)

            sender_addr = self.config.get_effective_sender()
            server.sendmail(sender_addr, [target_email], msg.as_string())
            server.quit()

            logger.info(f"Đã gửi email #{email_item.id} -> {target_email} ({email_item.category})")
            return True, f"Đã gửi thành công email #{email_item.id}"

        except Exception as e:
            err_msg = f"Thất bại khi gửi email #{email_item.id}: {str(e)}"
            logger.error(err_msg)
            return False, err_msg

    def send_batch(
        self,
        emails: List[GeneratedEmail],
        target_email: str,
        progress_callback: Optional[Callable[[int, int, GeneratedEmail, bool, str], None]] = None
    ) -> Dict[str, Any]:
        """
        Gửi hàng loạt danh sách email với độ trễ (rate limit) tùy chỉnh.
        Returns dict tổng kết kết quả.
        """
        total = len(emails)
        success_count = 0
        failed_count = 0
        logs = []

        logger.info(f"Bắt đầu quy trình gửi hàng loạt {total} email đến {target_email}...")

        for idx, email_item in enumerate(emails, start=1):
            success, msg = self.send_single(email_item, target_email)
            if success:
                success_count += 1
            else:
                failed_count += 1

            log_entry = {
                "index": idx,
                "timestamp": time.strftime("%H:%M:%S"),
                "email_id": email_item.id,
                "category": email_item.category,
                "subject": email_item.subject,
                "status": "Thành công" if success else "Thất bại",
                "detail": msg
            }
            logs.append(log_entry)

            if progress_callback:
                progress_callback(idx, total, email_item, success, msg)

            # Delay giữa các lần gửi để tránh bị khóa tài khoản SMTP hoặc dồn dập
            if idx < total and self.config.rate_limit_delay > 0:
                time.sleep(self.config.rate_limit_delay)

        return {
            "total": total,
            "success": success_count,
            "failed": failed_count,
            "logs": logs
        }

    def export_to_eml_files(self, emails: List[GeneratedEmail], target_email: str, output_dir: str = "eml_output") -> str:
        """Xuất danh sách email thành các tệp tin chuẩn .eml để test import cục bộ."""
        os.makedirs(output_dir, exist_ok=True)
        count = 0
        for email_item in emails:
            msg = self.build_mime_message(email_item, target_email)
            filename = f"{email_item.category}_{email_item.id}.eml"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(msg.as_string())
            count += 1
        return f"Đã xuất thành công {count} file .EML vào thư mục '{os.path.abspath(output_dir)}'"
