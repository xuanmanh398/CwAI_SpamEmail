import os
import json
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any

@dataclass
class SMTPConfig:
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    use_tls: bool = True
    use_ssl: bool = False
    username: str = ""
    password: str = ""
    sender_name: str = "EmailFlow Tester"
    sender_email: str = ""
    rate_limit_delay: float = 1.0  # seconds between emails
    dry_run: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SMTPConfig':
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    def get_effective_sender(self) -> str:
        if self.sender_email:
            return self.sender_email
        return self.username


# Standard presets for popular SMTP providers
SMTP_PRESETS = {
    "Gmail": {
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "use_tls": True,
        "use_ssl": False,
        "note": "Cần sử dụng 'Mật khẩu ứng dụng' (App Password) thay vì mật khẩu thông thường."
    },
    "Outlook / Office 365": {
        "smtp_server": "smtp.office365.com",
        "smtp_port": 587,
        "use_tls": True,
        "use_ssl": False,
        "note": "Cần kích hoạt SMTP AUTH trong cài đặt tài khoản."
    },
    "Mailtrap (Test Sandbox)": {
        "smtp_server": "sandbox.smtp.mailtrap.io",
        "smtp_port": 2525,
        "use_tls": True,
        "use_ssl": False,
        "note": "Dịch vụ giả lập SMTP miễn phí để test email an toàn không sợ bị coi là spam."
    },
    "Local MailHog / Test SMTP": {
        "smtp_server": "localhost",
        "smtp_port": 1025,
        "use_tls": False,
        "use_ssl": False,
        "note": "Server SMTP chạy cục bộ (Ví dụ: MailHog hoặc Python smtpd)."
    },
    "Chế độ Giả lập (Dry Run)": {
        "smtp_server": "localhost",
        "smtp_port": 25,
        "use_tls": False,
        "use_ssl": False,
        "dry_run": True,
        "note": "Không gửi qua mạng, chỉ tạo và ghi log email để kiểm tra nội dung."
    }
}
