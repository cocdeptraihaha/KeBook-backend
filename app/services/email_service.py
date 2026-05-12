"""Email service for sending OTP."""
import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import get_settings

settings = get_settings()


def _send_smtp_sync(email: str, otp_code: str, otp_type: str) -> bool:
    """Gửi email qua SMTP (blocking). Chạy trong thread, không block event loop."""
    msg = MIMEMultipart()
    msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
    msg["To"] = email
    msg["Subject"] = "KeBook account activation OTP" if otp_type == "activation" else "KeBook password reset OTP"
    body = f"""
    <html>
    <body>
        <p>Hello,</p>
        <p>Your OTP code is: <strong style="font-size: 24px; color: #667eea;">{otp_code}</strong></p>
        <p>This code will expire in {settings.OTP_EXPIRE_SECONDS} seconds.</p>
        <p>If you did not request this code, please ignore this email.</p>
        <hr>
        <p style="color: #666; font-size: 12px;">KeBook Store</p>
    </body>
    </html>
    """
    msg.attach(MIMEText(body, "html"))
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(msg)
    return True


class EmailService:
    """Service for sending OTP emails."""

    @staticmethod
    async def send_otp_email(email: str, otp_code: str, otp_type: str = "activation"):
        """Send email containing OTP. Chạy SMTP trong thread để không block event loop."""
        if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            print("[SMTP] SMTP_USER/SMTP_PASSWORD not configured - OTP email skipped.")
            return True

        try:
            await asyncio.to_thread(_send_smtp_sync, email, otp_code, otp_type)
            print(f"[SMTP] OTP email sent to {email}.")
            return True
        except Exception as e:
            print(f"[SMTP] Send failed: {e}")
            return False


email_service = EmailService()
