"""Auth endpoints: login, register với OTP, forgot password."""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import create_access_token, verify_password, get_password_hash
from app.models.otp import OTPType
from app.models.user import User
from app.schemas.user import User as UserSchema, UserCreate
from app.services.user_service import user_service
from app.services.otp_service import otp_service

router = APIRouter()
settings = get_settings()


class TokenResponse(BaseModel):
    """Response khi login thành công."""
    access_token: str
    token_type: str = "bearer"
    user: UserSchema


class RegisterResponse(BaseModel):
    """Response khi register thành công."""
    message: str
    email: str


class VerifyOTPRequest(BaseModel):
    """Request verify OTP."""
    email: EmailStr
    otp_code: str


class ForgotPasswordRequest(BaseModel):
    """Request forgot password."""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Request reset password."""
    email: EmailStr
    otp_code: str
    new_password: str


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Đăng ký user mới, gửi OTP qua email để kích hoạt."""
    try:
        # Tạo user với is_active=False
        user = await user_service.create_user(db, user_in)
        
        # Tạo và gửi OTP activation
        await otp_service.create_and_send_otp(
            db,
            user.email,
            OTPType.ACTIVATION,
        )
        await db.commit()
        
        return RegisterResponse(
            message="Đăng ký thành công! Vui lòng kiểm tra email để lấy mã OTP kích hoạt tài khoản.",
            email=user.email,
        )
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(
    request: VerifyOTPRequest,
    db: AsyncSession = Depends(get_db),
):
    """Verify OTP để kích hoạt tài khoản."""
    is_valid, otp = await otp_service.verify_otp(
        db,
        request.email,
        request.otp_code,
        OTPType.ACTIVATION,
    )

    if not is_valid:
        if otp and otp.is_expired():
            raise HTTPException(status_code=400, detail="Mã OTP đã hết hạn")
        raise HTTPException(status_code=400, detail="Mã OTP không hợp lệ")

    # Activate user
    user = await user_service.repository.get_by_email(db, request.email)
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy user")

    user.is_active = True
    await db.commit()
    await db.refresh(user)

    # Tạo token sau khi activate
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires,
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user,
    )


@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """Gửi OTP để reset password."""
    # Kiểm tra email có tồn tại không
    user = await user_service.repository.get_by_email(db, request.email)
    if not user:
        # Không tiết lộ email có tồn tại hay không (bảo mật)
        return {
            "message": "Nếu email tồn tại, chúng tôi đã gửi mã OTP đến email của bạn."
        }

    # Tạo và gửi OTP reset password
    await otp_service.create_and_send_otp(
        db,
        request.email,
        OTPType.RESET_PASSWORD,
    )
    await db.commit()

    return {
        "message": "Nếu email tồn tại, chúng tôi đã gửi mã OTP đến email của bạn."
    }


@router.post("/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """Reset password với OTP."""
    # Verify OTP
    is_valid, otp = await otp_service.verify_otp(
        db,
        request.email,
        request.otp_code,
        OTPType.RESET_PASSWORD,
    )

    if not is_valid:
        if otp and otp.is_expired():
            raise HTTPException(status_code=400, detail="Mã OTP đã hết hạn")
        raise HTTPException(status_code=400, detail="Mã OTP không hợp lệ")

    # Lấy user
    user = await user_service.repository.get_by_email(db, request.email)
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy user")

    # Update password
    user.hashed_password = get_password_hash(request.new_password)
    await db.commit()

    return {"message": "Đổi mật khẩu thành công! Vui lòng đăng nhập lại."}


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """Đăng nhập với JWT (email hoặc username + password)."""
    user = await user_service.repository.get_by_email_or_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email/username hoặc mật khẩu không đúng",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=400,
            detail="Tài khoản chưa được kích hoạt. Vui lòng kiểm tra email để lấy mã OTP.",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires,
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user,
    )
