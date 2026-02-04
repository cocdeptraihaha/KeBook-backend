"""Script test SMTP connection."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", SMTP_USER)

if not SMTP_USER or not SMTP_PASSWORD:
    print("❌ Chưa config SMTP_USER và SMTP_PASSWORD trong .env")
    print("\nVui lòng thêm vào file .env:")
    print("SMTP_USER=your-email@gmail.com")
    print("SMTP_PASSWORD=your-app-password")
    exit(1)

print(f"\n{'='*60}")
print("TEST SMTP CONNECTION")
print(f"{'='*60}")
print(f"SMTP Host: {SMTP_HOST}")
print(f"SMTP Port: {SMTP_PORT}")
print(f"SMTP User: {SMTP_USER}")
print(f"SMTP From: {SMTP_FROM_EMAIL}")
print(f"{'='*60}\n")

try:
    msg = MIMEMultipart()
    msg["From"] = SMTP_FROM_EMAIL
    msg["To"] = SMTP_USER  # Gửi cho chính mình để test
    msg["Subject"] = "Test SMTP - Backend Kebook"

    body = """
    <html>
    <body style="font-family: Arial, sans-serif;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #667eea;">✅ Test Email thành công!</h2>
            <p>Nếu bạn nhận được email này, SMTP đã được cấu hình đúng.</p>
            <p>Bạn có thể sử dụng SMTP để gửi OTP cho users.</p>
            <hr>
            <p style="color: #666; font-size: 12px;">Backend Kebook API</p>
        </div>
    </body>
    </html>
    """
    msg.attach(MIMEText(body, "html"))

    print("📧 Đang kết nối đến SMTP server...")
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        print("🔐 Đang bật TLS...")
        server.starttls()
        print("🔑 Đang đăng nhập...")
        server.login(SMTP_USER, SMTP_PASSWORD)
        print("📤 Đang gửi email...")
        server.send_message(msg)
    
    print(f"\n✅ Gửi email thành công!")
    print(f"📬 Kiểm tra hộp thư của {SMTP_USER}")
    print(f"   (Có thể trong Spam/Junk folder)\n")
except smtplib.SMTPAuthenticationError as e:
    print(f"\n❌ Lỗi xác thực: {e}")
    print("\nKiểm tra:")
    print("1. SMTP_USER và SMTP_PASSWORD đúng chưa?")
    print("2. Nếu dùng Gmail: Đã tạo App Password chưa?")
    print("3. App Password có đúng 16 ký tự không?")
except smtplib.SMTPConnectError as e:
    print(f"\n❌ Lỗi kết nối: {e}")
    print("\nKiểm tra:")
    print(f"1. SMTP_HOST đúng chưa? (hiện tại: {SMTP_HOST})")
    print(f"2. SMTP_PORT đúng chưa? (hiện tại: {SMTP_PORT})")
    print("3. Firewall có chặn port không?")
except Exception as e:
    print(f"\n❌ Lỗi: {e}")
    print("\nXem hướng dẫn trong file HUONG_DAN_SETUP_SMTP.md")
