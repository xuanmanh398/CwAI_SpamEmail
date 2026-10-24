import streamlit as st
import pandas as pd
import time
import os
import json

from config import SMTPConfig, SMTP_PRESETS
from email_generator import EmailGenerator, EMAIL_CATEGORIES, GeneratedEmail
from email_sender import EmailSender

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="EmailFlow Automated Tester",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E88E5;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #555;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        border-left: 4px solid #1E88E5;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .stProgress > div > div > div > div {
        background-color: #1E88E5;
    }
    </style>
""", unsafe_allow_html=True)

# Main Title Header
st.markdown('<div class="main-header">📧 EmailFlow - Automated Multi-Email Classifier Tester</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Phần mềm tự động tạo và gửi hàng loạt Email đa phân loại để kiểm tra khả năng nhận diện của EmailFlow</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# SIDEBAR - CẤU HÌNH MÁY CHỦ SMTP
# ---------------------------------------------------------
st.sidebar.header("⚙️ Cấu hình Máy Chủ SMTP")

preset_name = st.sidebar.selectbox(
    "Chọn Mẫu SMTP Có Sẵn (Preset):",
    options=list(SMTP_PRESETS.keys()),
    index=0
)

selected_preset = SMTP_PRESETS[preset_name]
st.sidebar.info(selected_preset.get("note", ""))

is_dry_run = selected_preset.get("dry_run", False)

if not is_dry_run:
    smtp_server = st.sidebar.text_input("SMTP Server Host:", value=selected_preset["smtp_server"])
    smtp_port = st.sidebar.number_input("SMTP Port:", value=selected_preset["smtp_port"], step=1)
    use_tls = st.sidebar.checkbox("Sử dụng TLS (STARTTLS)", value=selected_preset["use_tls"])
    use_ssl = st.sidebar.checkbox("Sử dụng SSL direct", value=selected_preset["use_ssl"])
    
    sender_name = st.sidebar.text_input("Tên Người Gửi (Display Name):", value="EmailFlow Tester")
    smtp_username = st.sidebar.text_input("SMTP Username / Email:", value="")
    smtp_password = st.sidebar.text_input("SMTP Password / App Password:", value="", type="password")
    sender_email = st.sidebar.text_input("Email Người Gửi (tùy chọn):", value="")
else:
    smtp_server = "localhost"
    smtp_port = 25
    use_tls = False
    use_ssl = False
    sender_name = "DryRun Tester"
    smtp_username = ""
    smtp_password = ""
    sender_email = "dryrun@emailflow.test"
    st.sidebar.warning("⚠️ Đang ở chế độ Dry Run: Email sẽ được tạo và ghi log hoàn chỉnh nhưng KHÔNG gửi qua mạng.")

rate_delay = st.sidebar.slider("⏱️ Trễ giữa mỗi lần gửi (giây):", min_value=0.0, max_value=5.0, value=1.0, step=0.5)

# Khởi tạo Config Object
app_config = SMTPConfig(
    smtp_server=smtp_server,
    smtp_port=int(smtp_port),
    use_tls=use_tls,
    use_ssl=use_ssl,
    username=smtp_username,
    password=smtp_password,
    sender_name=sender_name,
    sender_email=sender_email,
    rate_limit_delay=rate_delay,
    dry_run=is_dry_run
)

sender_engine = EmailSender(app_config)

# Nút test kết nối
if st.sidebar.button("🔍 Kiểm Tra Kết Nối SMTP", use_container_width=True):
    with st.spinner("Đang thử kết nối máy chủ..."):
        ok, msg = sender_engine.test_connection()
        if ok:
            st.sidebar.success(msg)
        else:
            st.sidebar.error(msg)

st.sidebar.markdown("---")
st.sidebar.caption("Phiên bản: 1.0.0 | Antigravity AI Suite")

# ---------------------------------------------------------
# TABS GIAO DIỆN CHÍNH
# ---------------------------------------------------------
tab_run, tab_preview, tab_eml, tab_docs = st.tabs([
    "🚀 Gửi Test Hàng Loạt",
    "📋 Xem Trước Mẫu Email",
    "📦 Xuất File .EML",
    "ℹ️ Hướng Dẫn Cấu Hình"
])

# =========================================================
# TAB 1: GỬI TEST HÀNG LOẠT
# =========================================================
with tab_run:
    col_input1, col_input2 = st.columns([2, 1])

    with col_input1:
        target_email = st.text_input(
            "🎯 Địa chỉ Email Nhận (Recipient Target):",
            placeholder="vd: classifier@emailflow.internal hoặc test-target@gmail.com",
            help="Đây là email mà EmailFlow sẽ đứng nhận hoặc theo dõi inbox để phân loại."
        )

        all_cat_keys = list(EMAIL_CATEGORIES.keys())
        selected_categories = st.multiselect(
            "🏷️ Chọn Các Danh Mục Phân Loại Để Gửi:",
            options=all_cat_keys,
            default=all_cat_keys,
            format_func=lambda x: f"{x} - {EMAIL_CATEGORIES[x]['label']}"
        )

    with col_input2:
        email_count = st.number_input("🔢 Số Lượng Email Cần Gửi:", min_value=1, max_value=200, value=20, step=5)
        
        custom_kw_input = st.text_input(
            "🏷️ Tag/Từ Khóa Tùy Chỉnh (Cách nhau bằng dấu phẩy):",
            placeholder="vd: URGENT, INVOICE, TICKET",
            help="Chèn thêm từ khóa vào tiêu đề/nội dung để kiểm tra bộ lọc từ khóa của EmailFlow."
        )

    st.markdown("### ⚡ Kịch Bản Test Nhanh (Quick Test Presets)")
    col_p1, col_p2, col_p3 = st.columns(3)

    if col_p1.button("🧪 Stress Test Đa Phân Loại (30 Email Mix)"):
        st.session_state['quick_count'] = 30
        st.session_state['quick_cats'] = all_cat_keys
        st.rerun()

    if col_p2.button("🛡️ Test Bộ Lọc Spam & Phishing (15 Email)"):
        st.session_state['quick_count'] = 15
        st.session_state['quick_cats'] = ["SPAM", "PHISHING"]
        st.rerun()

    if col_p3.button("💼 Test Router Hóa Đơn & Dự Án (20 Email)"):
        st.session_state['quick_count'] = 20
        st.session_state['quick_cats'] = ["WORK", "FINANCE", "SUPPORT"]
        st.rerun()

    if 'quick_count' in st.session_state:
        email_count = st.session_state.pop('quick_count')
    if 'quick_cats' in st.session_state:
        selected_categories = st.session_state.pop('quick_cats')

    st.markdown("---")

    # Nút Bắt Đầu Gửi
    start_test = st.button("🚀 BẮT ĐẦU CHẠY TEST EMAILFLOW", type="primary", use_container_width=True)

    if start_test:
        if not target_email:
            st.error("⚠️ Vui lòng nhập Địa chỉ Email Nhận trước khi bắt đầu!")
        elif not selected_categories:
            st.error("⚠️ Vui lòng chọn ít nhất 1 danh mục phân loại email!")
        else:
            custom_kws = [k.strip() for k in custom_kw_input.split(",") if k.strip()] if custom_kw_input else None
            
            st.info(f"⏳ Đang chuẩn bị tạo batch {email_count} email cho {len(selected_categories)} phân loại...")

            # Tạo danh sách email
            test_batch = EmailGenerator.generate_batch(
                count=email_count,
                target_email=target_email,
                categories=selected_categories,
                custom_keywords=custom_kws
            )

            # Component hiển thị Tiến độ
            progress_bar = st.progress(0.0)
            status_text = st.empty()

            # Dynamic Metrics Layout
            m_col1, m_col2, m_col3, m_col4 = st.columns(4)
            metric_sent = m_col1.metric("Đã xử lý", f"0/{email_count}")
            metric_success = m_col2.metric("Thành công ✅", "0")
            metric_failed = m_col3.metric("Thất bại ❌", "0")
            metric_cat_count = m_col4.metric("Số Phân Loại", len(selected_categories))

            log_table_placeholder = st.empty()

            logs_list = []
            success_counter = 0
            failed_counter = 0

            # Tiến hành gửi từng email
            for idx, email_item in enumerate(test_batch, start=1):
                status_text.markdown(f"**Đang gửi [{idx}/{email_count}]:** `{email_item.category}` - *{email_item.subject[:50]}...*")

                ok, msg_detail = sender_engine.send_single(email_item, target_email)
                if ok:
                    success_counter += 1
                else:
                    failed_counter += 1

                logs_list.append({
                    "STT": idx,
                    "Thời Gian": time.strftime("%H:%M:%S"),
                    "ID Email": email_item.id,
                    "Danh Mục": email_item.category,
                    "Tiêu Đề": email_item.subject,
                    "Trạng Thái": "✅ Thành công" if ok else "❌ Thất bại",
                    "Chi Tiết": msg_detail
                })

                # Cập nhật UI
                progress = idx / email_count
                progress_bar.progress(progress)
                
                metric_sent.metric("Đã xử lý", f"{idx}/{email_count}")
                metric_success.metric("Thành công ✅", f"{success_counter}")
                metric_failed.metric("Thất bại ❌", f"{failed_counter}")

                # Hiển thị bảng log real-time
                df_logs = pd.DataFrame(logs_list)
                log_table_placeholder.dataframe(df_logs, use_container_width=True)

                if idx < email_count and app_config.rate_limit_delay > 0:
                    time.sleep(app_config.rate_limit_delay)

            status_text.markdown("### 🎉 HOÀN THÀNH QUY TRÌNH TEST!")
            st.balloons()
            st.success(f"Đã hoàn thành gửi {email_count} email test đến **{target_email}**. Kiểm tra hộp thư EmailFlow để xác nhận khả năng phân loại!")

# =========================================================
# TAB 2: XEM TRƯỚC MẪU EMAIL
# =========================================================
with tab_preview:
    st.markdown("### 📋 Trình Xem Trước Nội Dung Email Mẫu (Template Inspector)")
    st.caption("Khám phá các mẫu email ngẫu nhiên sẽ được sinh ra cho mỗi danh mục phân loại.")

    preview_cat = st.selectbox(
        "Chọn Danh Mục Phân Loại Để Xem Mẫu:",
        options=list(EMAIL_CATEGORIES.keys()),
        format_func=lambda x: f"{x} - {EMAIL_CATEGORIES[x]['label']}"
    )

    if st.button("🎲 Sinh Mẫu Email Ngẫu Nhiên Mới"):
        st.rerun()

    sample_email = EmailGenerator.generate_single_email(
        category=preview_cat,
        target_email="test-preview@emailflow.internal",
        custom_keywords=["DEMO_TAG"]
    )

    col_meta1, col_meta2 = st.columns(2)
    with col_meta1:
        st.markdown(f"**Category:** `{sample_email.category}`")
        st.markdown(f"**From Name:** `{sample_email.sender_name}`")
        st.markdown(f"**Priority:** `{sample_email.priority}`")
    with col_meta2:
        st.markdown(f"**Subject:** `{sample_email.subject}`")
        st.markdown(f"**Custom Headers:**")
        st.json(sample_email.headers)

    st.markdown("#### 📧 Hiển thị Nội dung HTML:")
    st.components.v1.html(sample_email.body_html, height=280, scrolling=True)

    with st.expander("📄 View Plain Text Body"):
        st.code(sample_email.body_text, language="text")

# =========================================================
# TAB 3: XUẤT FILE .EML
# =========================================================
with tab_eml:
    st.markdown("### 📦 Xuất Email Ra File Cục Bộ (.EML)")
    st.markdown("Nếu hệ thống **EmailFlow** hỗ trợ test phân loại qua thư mục hoặc đọc file trực tiếp mà không cần qua SMTP, bạn có thể xuất các tệp `.eml` tại đây.")

    eml_count = st.number_input("Số lượng file .eml cần tạo:", min_value=1, max_value=100, value=10)
    eml_target = st.text_input("Địa chỉ Email người nhận ghi trong file:", value="eml-test@emailflow.internal")
    eml_out_dir = st.text_input("Thư mục lưu trữ output:", value="eml_output")

    if st.button("💾 Bắt Đầu Xuất File .EML"):
        eml_batch = EmailGenerator.generate_batch(eml_count, eml_target)
        msg_result = sender_engine.export_to_eml_files(eml_batch, eml_target, eml_out_dir)
        st.success(msg_result)

        # Liệt kê các file vừa tạo
        if os.path.exists(eml_out_dir):
            files = os.listdir(eml_out_dir)
            st.markdown(f"**Các file đã được lưu tại `{os.path.abspath(eml_out_dir)}`:**")
            st.write(files[:20])

# =========================================================
# TAB 4: HƯỚNG DẪN CẤU HÌNH
# =========================================================
with tab_docs:
    st.markdown("""
    ### 📖 Hướng Dẫn Chi Tiết Cấu Hình Gửi Email Test

    #### 1. Cấu Hình Gửi Qua Gmail
    - Đăng nhập tài khoản Google -> Quản lý Tài Khoản Google -> **Bảo mật** (Security).
    - Bật **Xác minh 2 bước** (2-Step Verification).
    - Tìm kiếm **Mật khẩu ứng dụng** (App Passwords) -> Tạo mật khẩu mới cho ứng dụng Email.
    - Nhập 16 ký tự mật khẩu ứng dụng vào ô **SMTP Password** trên thanh bên trái.
    - Host: `smtp.gmail.com` | Port: `587` | Tick chọn `TLS`.

    #### 2. Cấu Hình Gửi An Toàn Qua Mailtrap Sandbox (Khuyên Dùng)
    - Truy cập [mailtrap.io](https://mailtrap.io) và đăng ký tài khoản miễn phí.
    - Tạo 1 Inbox thử nghiệm -> Lấy thông số `Username` và `Password` SMTP.
    - Mailtrap sẽ bắt giữ tất cả email gửi đến trong giao diện giả lập, hoàn toàn an toàn và không lo bị khóa tài khoản thật.

    #### 3. Chế Độ Dry Run (Giả Lập Cục Bộ)
    - Chọn preset **Chế độ Giả lập (Dry Run)** trên thanh công cụ.
    - Trong chế độ này, phần mềm tạo ra cấu trúc email hoàn chỉnh (Text, HTML, Headers) và mô phỏng độ trễ như gửi thật nhưng không tốn băng thông và không cần cấu hình mạng.

    #### 4. Cách Đánh Giá Khả Năng Phân Loại Của EmailFlow
    - Gửi thử một batch gồm 30-50 email pha trộn nhiều danh mục.
    - Kiểm tra bảng điều khiển EmailFlow xem:
      - Các email `SPAM` và `PHISHING` có bị đưa vào Junk/Spam folder không?
      - Email `FINANCE` / `WORK` có được gán nhãn hoặc điều hướng đúng bộ phận?
      - Thời gian phản hồi của bộ classifier khi nhận dồn dập nhiều email.
    """)
