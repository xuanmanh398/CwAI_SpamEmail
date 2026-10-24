import argparse
import sys
import os
import time
from typing import List

from config import SMTPConfig, SMTP_PRESETS
from email_generator import EmailGenerator, EMAIL_CATEGORIES
from email_sender import EmailSender

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def print_banner():
    print("=" * 65)
    print(" 🚀 EMAILFLOW TESTER - TỰ ĐỘNG GỬI EMAIL THỬ NGHIỆM PHÂN LOẠI")
    print("=" * 65)

def run_interactive_cli():
    print_banner()
    print("\n--- Cấu hình Máy Chủ SMTP ---")
    print("1. Chế độ Giả lập (Dry Run - Không cần tài khoản SMTP)")
    print("2. Dùng Mailtrap Sandbox (An toàn)")
    print("3. Dùng Gmail (Yêu cầu App Password)")
    print("4. Nhập thông số SMTP tùy chỉnh")
    
    choice = input("\nChọn cấu hình [1-4] (Mặc định 1): ").strip() or "1"
    
    config = SMTPConfig()
    
    if choice == "1":
        config.dry_run = True
        print("✅ Đã chọn chế độ Giả lập (Dry Run).")
    elif choice == "2":
        preset = SMTP_PRESETS["Mailtrap (Test Sandbox)"]
        config.smtp_server = preset["smtp_server"]
        config.smtp_port = preset["smtp_port"]
        config.username = input("Nhập Mailtrap Username: ").strip()
        config.password = input("Nhập Mailtrap Password: ").strip()
    elif choice == "3":
        config.smtp_server = "smtp.gmail.com"
        config.smtp_port = 587
        config.use_tls = True
        config.username = input("Nhập Địa chỉ Gmail: ").strip()
        config.password = input("Nhập Gmail App Password (16 ký tự): ").strip()
    else:
        config.smtp_server = input("SMTP Server: ").strip()
        config.smtp_port = int(input("SMTP Port (vd 587): ").strip() or "587")
        config.username = input("Username (tùy chọn): ").strip()
        config.password = input("Password (tùy chọn): ").strip()

    target_email = input("\n📧 Nhập địa chỉ Email nhận (Recipient): ").strip()
    if not target_email:
        target_email = "test-target@emailflow.internal"
        print(f"Sử dụng địa chỉ nhận mặc định: {target_email}")

    print("\n--- Danh sách Phân loại Email (Categories) ---")
    cat_keys = list(EMAIL_CATEGORIES.keys())
    for idx, k in enumerate(cat_keys, start=1):
        print(f"{idx}. {k} ({EMAIL_CATEGORIES[k]['label']})")
    print(f"{len(cat_keys) + 1}. TẤT CẢ PHÂN LOẠI (Pha trộn ngẫu nhiên)")

    cat_choice = input(f"Chọn danh mục [1-{len(cat_keys) + 1}] (Mặc định ALL): ").strip()
    selected_cats = []
    if cat_choice.isdigit() and 1 <= int(cat_choice) <= len(cat_keys):
        selected_cats = [cat_keys[int(cat_choice) - 1]]
    else:
        selected_cats = cat_keys

    count_str = input("\n🔢 Nhập số lượng email muốn gửi (Mặc định 10): ").strip()
    count = int(count_str) if count_str.isdigit() else 10

    delay_str = input("⏱️  Thời gian chờ giữa mỗi email (giây, Mặc định 1.0): ").strip()
    config.rate_limit_delay = float(delay_str) if delay_str else 1.0

    print("\n-----------------------------------------------------------")
    print(f"Tổng kết kịch bản test:")
    print(f"- Số lượng: {count} email")
    print(f"- Phân loại: {', '.join(selected_cats)}")
    print(f"- Email nhận: {target_email}")
    print(f"- Trễ giữa mỗi lần gửi: {config.rate_limit_delay}s")
    print(f"- Trạng thái: {'DRY RUN (Giả lập)' if config.dry_run else 'GỬI THỰC TẾ OVER SMTP'}")
    print("-----------------------------------------------------------")

    confirm = input("▶️ Bạn có muốn bắt đầu gửi ngay không? (y/n): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("Đã hủy thao tác.")
        return

    sender = EmailSender(config)
    
    # Kiểm tra kết nối trước khi gửi
    ok, msg = sender.test_connection()
    print(f"\n[Kiểm tra máy chủ] {msg}")
    if not ok:
        print("❌ Hủy tiến trình do lỗi kết nối SMTP.")
        return

    print("\n🚀 Đang tiến hành tạo và gửi email...\n")
    emails = EmailGenerator.generate_batch(count, target_email, selected_cats)

    def on_progress(idx, total, email_obj, success, detail):
        status_icon = "✅" if success else "❌"
        print(f"[{idx}/{total}] {status_icon} [{email_obj.category:<9}] {email_obj.subject[:45]}...")

    result = sender.send_batch(emails, target_email, progress_callback=on_progress)

    print("\n===========================================================")
    print(f"🎉 HOÀN THÀNH TEST EMAILFLOW!")
    print(f"Tổng số: {result['total']} | Thành công: {result['success']} | Thất bại: {result['failed']}")
    print("===========================================================")


def main():
    parser = argparse.ArgumentParser(description="EmailFlow Tester - Tool tự động gửi nhiều email phân loại để test EmailFlow.")
    parser.add_argument("-t", "--target", type=str, help="Email người nhận (Recipient)")
    parser.add_argument("-n", "--count", type=int, default=10, help="Số lượng email cần gửi")
    parser.add_argument("-c", "--category", type=str, default="ALL", help="Danh mục email (SPAM, PHISHING, WORK, FINANCE, SUPPORT, NEWSLETTER, URGENT, ALL)")
    parser.add_argument("-d", "--delay", type=float, default=1.0, help="Thời gian trễ giữa các lần gửi (giây)")
    parser.add_argument("--dry-run", action="store_true", help="Bật chế độ giả lập gửi (không gửi qua SMTP)")
    parser.add_argument("--export-eml", action="store_true", help="Xuất email ra các tệp .eml cục bộ")
    parser.add_argument("--smtp-server", type=str, default="smtp.gmail.com", help="Địa chỉ SMTP server")
    parser.add_argument("--smtp-port", type=int, default=587, help="Cổng SMTP server")
    parser.add_argument("--username", type=str, help="Tài khoản đăng nhập SMTP")
    parser.add_argument("--password", type=str, help="Mật khẩu / App Password SMTP")

    args = parser.parse_args()

    # Nếu không truyền tham số CLI thì chạy menu tương tác
    if len(sys.argv) == 1:
        run_interactive_cli()
        return

    config = SMTPConfig(
        smtp_server=args.smtp_server,
        smtp_port=args.smtp_port,
        username=args.username or "",
        password=args.password or "",
        rate_limit_delay=args.delay,
        dry_run=args.dry_run
    )

    categories = [args.category.upper()] if args.category.upper() != "ALL" else None
    target_email = args.target or "test-recipient@emailflow.internal"

    print_banner()
    print(f"Khởi động test CLI cho EmailFlow...")
    emails = EmailGenerator.generate_batch(args.count, target_email, categories)

    sender = EmailSender(config)

    if args.export_eml:
        msg = sender.export_to_eml_files(emails, target_email)
        print(f"📦 {msg}")
        return

    def on_progress(idx, total, email_obj, success, detail):
        status_icon = "✅" if success else "❌"
        print(f"[{idx}/{total}] {status_icon} [{email_obj.category:<9}] {email_obj.subject[:50]}...")

    result = sender.send_batch(emails, target_email, progress_callback=on_progress)
    print(f"\n🎉 Hoàn tất: {result['success']}/{result['total']} email thành công.")

if __name__ == "__main__":
    main()
