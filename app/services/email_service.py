"""Email service để gửi OTP."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import get_settings

settings = get_settings()


class EmailService:
    """Service gửi email OTP."""

    @staticmethod
    async def send_otp_email(email: str, otp_code: str, otp_type: str = "activation"):
        """Gửi email chứa OTP."""
        if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            # Development mode: in OTP ra console thay vì gửi email
            print(f"\n[SMTP] Không cấu hình SMTP_USER/SMTP_PASSWORD - in OTP ra console:")
            print(f"  OTP cho {email}: {otp_code} (loại: {otp_type})")
            print()
            return True

        print(f"[SMTP] Đang gửi email OTP tới {email} ...")
        try:
            msg = MIMEMultipart()
            msg["From"] = settings.SMTP_FROM_EMAIL or settings.SMTP_USER
            msg["To"] = email
            msg["Subject"] = "Mã OTP kích hoạt tài khoản" if otp_type == "activation" else "Mã OTP reset mật khẩu"

            body = f"""
            <html>
            <body>
                <h2>Mã OTP của bạn</h2>
                <p>Xin chào,</p>
                <p>Mã OTP của bạn là: <strong style="font-size: 24px; color: #667eea;">{otp_code}</strong></p>
                <p>Mã này sẽ hết hạn sau {settings.OTP_EXPIRE_SECONDS} giây.</p>
                <p>Nếu bạn không yêu cầu mã này, vui lòng bỏ qua email này.</p>
                <hr>
                <p style="color: #666; font-size: 12px;">Backend Kebook API</p>
            </body>
            </html>
            """
            msg.attach(MIMEText(body, "html"))

            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)

            print(f"[SMTP] Đã gửi email OTP tới {email}.")
            return True
        except Exception as e:
            print(f"[SMTP] Lỗi gửi email: {e}")
            # Development: vẫn in OTP ra console
            print(f"\n{'='*50}")
            print(f"OTP cho {email}: {otp_code}")
            print(f"{'='*50}\n")
            return False


email_service = EmailService()
