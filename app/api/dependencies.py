"""Shared API dependencies (auth, etc.)."""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import ALGORITHM
from app.models.user import User
from app.repositories.user_repository import user_repository

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False,
)


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:
    """Get current user from JWT."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise _unauthorized("Invalid token: missing subject")
        user_id = int(user_id)
    except (JWTError, ValueError):
        raise _unauthorized("Invalid or expired token")

    user = await user_repository.get(db, user_id)
    if user is None:
        raise _unauthorized("User not found")

    if getattr(user, "deleted_at", None) is not None:
        raise _unauthorized("Account has been deleted")
    return user


async def get_current_user_optional(
    db: AsyncSession = Depends(get_db),
    token: str | None = Depends(oauth2_scheme_optional),
) -> User | None:
    """Có token hợp lệ thì trả user, không thì None (không raise)."""
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            return None
        user_id = int(user_id)
    except (JWTError, ValueError):
        return None
    user = await user_repository.get(db, user_id)
    if user is None or getattr(user, "deleted_at", None) is not None:
        return None
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Ensure user is active."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account not activated.",
        )
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """Ensure user is superuser (admin)."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions.",
        )
    return current_user
