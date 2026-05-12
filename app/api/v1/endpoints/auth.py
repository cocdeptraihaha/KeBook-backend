"""Auth endpoints: login, register with OTP, forgot password."""
import logging
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr

from app.core.config import get_settings
from app.core.ratelimit import limiter

logger = logging.getLogger(__name__)
from app.core.database import get_db
from app.core.security import create_access_token, verify_password
from app.models.otp import OTPType
from app.models.user import User
from app.schemas.user import User as UserSchema, UserCreate
from app.services.user_service import user_service
from app.services.otp_service import otp_service

router = APIRouter()
settings = get_settings()


class TokenResponse(BaseModel):
    """Response when login successful."""
    access_token: str
    token_type: str = "bearer"
    user: UserSchema


class RegisterResponse(BaseModel):
    """Response when register successful."""
    message: str
    email: str


class VerifyOTPRequest(BaseModel):
    """Request verify OTP."""
    email: EmailStr
    otp_code: str


class ResendOTPRequest(BaseModel):
    """Request resend activation OTP."""
    email: EmailStr


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
    try:
        user = await user_service.create_user(db, user_in)

        await otp_service.create_and_send_otp(
            db,
            user.email,
            OTPType.ACTIVATION,
        )
        await db.commit()

        return RegisterResponse(
            message="Registration successful. Please check your email for the OTP activation code.",
            email=user.email,
        )
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        await db.rollback()
        logger.exception("register error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/verify-otp", response_model=TokenResponse)
@limiter.limit("10/minute")
async def verify_otp(
    request_http: Request,
    request: VerifyOTPRequest,
    db: AsyncSession = Depends(get_db),
):
    """Verify OTP to activate account."""
    try:
        is_valid, otp = await otp_service.verify_otp(
            db,
            request.email,
            request.otp_code,
            OTPType.ACTIVATION,
        )

        if not is_valid:
            if otp and otp.is_expired():
                raise HTTPException(status_code=400, detail="OTP code has expired")
            raise HTTPException(status_code=400, detail="Invalid OTP code")

        user = await user_service.repository.get_by_email(db, request.email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        await user_service.activate_user(db, user.id)

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expires,
        )

        user_schema = UserSchema.model_validate(user)
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_schema,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("verify_otp error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/resend-otp")
@limiter.limit("5/minute")
async def resend_otp(
    request_http: Request,
    request: ResendOTPRequest,
    db: AsyncSession = Depends(get_db),
):
    """Resend activation OTP. Chỉ gửi nếu email tồn tại và chưa kích hoạt; email lạ vẫn 200 (bảo mật)."""
    user = await user_service.repository.get_by_email(db, request.email)
    if not user or user.deleted_at is not None:
        return {
            "message": "If this email is registered and not activated, an OTP has been sent."
        }
    if user.is_active:
        raise HTTPException(status_code=400, detail="Account already activated")

    await otp_service.create_and_send_otp(
        db,
        request.email,
        OTPType.ACTIVATION,
    )
    await db.commit()

    return {
        "message": "New OTP sent. Please check your email to activate your account."
    }


@router.post("/forgot-password")
@limiter.limit("5/minute")
async def forgot_password(
    request_http: Request,
    request: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """Send OTP to reset password. Only sends if email exists in DB."""
    user = await user_service.repository.get_by_email(db, request.email)
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")

    await otp_service.create_and_send_otp(
        db,
        request.email,
        OTPType.RESET_PASSWORD,
    )
    await db.commit()

    return {
        "message": "OTP has been sent to your email."
    }


@router.post("/reset-password")
@limiter.limit("10/minute")
async def reset_password(
    request_http: Request,
    request: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """Reset password with OTP."""
    # Verify OTP
    is_valid, otp = await otp_service.verify_otp(
        db,
        request.email,
        request.otp_code,
        OTPType.RESET_PASSWORD,
    )

    if not is_valid:
        if otp and otp.is_expired():
            raise HTTPException(status_code=400, detail="OTP code has expired")
        raise HTTPException(status_code=400, detail="Invalid OTP code")

    user = await user_service.repository.get_by_email(db, request.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await user_service.reset_password(db, user.id, request.new_password)

    return {"message": "Password changed successfully. Please log in again."}


@router.post("/login", response_model=TokenResponse)
@limiter.limit("30/minute")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """Login with JWT (email or username + password)."""
    user = await user_service.repository.get_by_email_or_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email/username or password",
        )

    if user.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account has been deactivated",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=400,
            detail="Account not activated. Please check your email for the OTP code.",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires,
    )

    user_schema = UserSchema.model_validate(user)
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_schema,
    )
