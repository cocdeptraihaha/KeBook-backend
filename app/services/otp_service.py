"""OTP service: tạo và verify OTP."""
import random
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete

from app.models.otp import OTP, OTPType
from app.models.user import User
from app.core.config import get_settings
from app.services.email_service import email_service

settings = get_settings()


class OTPService:
    """Service xử lý OTP."""

    @staticmethod
    def generate_otp() -> str:
        """Tạo OTP code 6 số."""
        return str(random.randint(100000, 999999))

    async def delete_expired_otps(self, db: AsyncSession) -> int:
        """Xóa tất cả OTP đã hết hạn. Trả về số bản ghi đã xóa."""
        result = await db.execute(delete(OTP).where(OTP.expires_at < datetime.utcnow()))
        return result.rowcount

    async def cleanup_expired_otps_and_inactive_users(
        self, db: AsyncSession
    ) -> tuple[int, int]:
        """Xóa user chưa kích hoạt (is_active=False) có OTP kích hoạt đã hết hạn, rồi xóa OTP hết hạn. Trả về (số user đã xóa, số OTP đã xóa)."""
        now = datetime.utcnow()
        # Lấy email có OTP kích hoạt đã hết hạn
        result = await db.execute(
            select(OTP.email).where(
                OTP.expires_at < now,
                OTP.otp_type == OTPType.ACTIVATION,
            ).distinct()
        )
        emails = [row[0] for row in result.fetchall()]
        users_deleted = 0
        for email in emails:
            r = await db.execute(select(User).where(User.email == email, User.is_active == False))
            user = r.scalars().first()
            if user:
                await db.delete(user)
                users_deleted += 1
        await db.flush()
        otps_deleted = (await self.delete_expired_otps(db)) or 0
        return users_deleted, otps_deleted

    async def create_and_send_otp(
        self,
        db: AsyncSession,
        email: str,
        otp_type: OTPType,
    ) -> str:
        """Tạo OTP, lưu vào DB và gửi email."""
        # Xóa user chưa kích hoạt có OTP hết hạn + xóa OTP hết hạn trước khi tạo mới
        await self.cleanup_expired_otps_and_inactive_users(db)

        # Tạo OTP mới
        otp_code = self.generate_otp()
        expires_at = datetime.utcnow() + timedelta(seconds=settings.OTP_EXPIRE_SECONDS)

        otp = OTP(
            email=email,
            code=otp_code,
            otp_type=otp_type,
            expires_at=expires_at,
        )
        db.add(otp)
        await db.flush()

        # Gửi email
        await email_service.send_otp_email(
            email,
            otp_code,
            otp_type.value,
        )

        return otp_code

    async def verify_otp(
        self,
        db: AsyncSession,
        email: str,
        code: str,
        otp_type: OTPType,
    ) -> tuple[bool, OTP | None]:
        """Verify OTP. Trả về (is_valid, otp_object)."""
        result = await db.execute(
            select(OTP).where(
                and_(
                    OTP.email == email,
                    OTP.code == code,
                    OTP.otp_type == otp_type,
                    OTP.is_used == False,
                )
            ).order_by(OTP.created_at.desc())
        )
        otp = result.scalars().first()

        if not otp:
            return False, None

        if otp.is_expired():
            return False, otp

        # Đánh dấu đã dùng
        otp.is_used = True
        await db.flush()

        return True, otp


otp_service = OTPService()
