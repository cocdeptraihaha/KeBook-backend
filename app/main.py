"""Application entry point."""
import asyncio
import sys
from contextlib import asynccontextmanager

# Fix Windows console: UTF-8 cho Vietnamese
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from fastapi_pagination import add_pagination

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.api.ws_notifications import router as ws_notifications_router
from app.core.database import database, AsyncSessionLocal
from app.core.ratelimit import limiter
from app.services.otp_service import otp_service

# Chu kỳ xóa OTP hết hạn (giây)
OTP_CLEANUP_INTERVAL = 60


def _parse_cors_origins(raw: str) -> list[str]:
    origins = [item.strip() for item in (raw or "").split(",")]
    return [item for item in origins if item]


async def _periodic_otp_cleanup(stopped: asyncio.Event):
    """Chạy nền: định kỳ xóa OTP hết hạn và user chưa kích hoạt có OTP hết hạn."""
    while not stopped.is_set():
        try:
            async with AsyncSessionLocal() as session:
                users_n, otps_n = await otp_service.cleanup_expired_otps_and_inactive_users(session)
                await session.commit()
                if users_n > 0 or otps_n > 0:
                    if users_n > 0:
                        print(f"[OTP] Deleted {users_n} inactive users (OTP expired).")
                    if otps_n > 0:
                        print(f"[OTP] Deleted {otps_n} expired OTP codes.")
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"[OTP] Error cleaning OTP/users: {e}")
        await asyncio.sleep(OTP_CLEANUP_INTERVAL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    await database.connect()
    # Xóa OTP hết hạn và user chưa kích hoạt có OTP hết hạn khi khởi động
    async with AsyncSessionLocal() as session:
        await otp_service.cleanup_expired_otps_and_inactive_users(session)
        await session.commit()
    # Chạy task định kỳ xóa OTP hết hạn
    stop_cleanup = asyncio.Event()
    cleanup_task = asyncio.create_task(_periodic_otp_cleanup(stop_cleanup))
    yield
    stop_cleanup.set()
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass
    await database.disconnect()


app = FastAPI(
    title="Backend Kebook API",
    version="1.0.0",
    description="API template với FastAPI, async và dependency injection",
    lifespan=lifespan,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

settings = get_settings()
cors_origins = _parse_cors_origins(settings.CORS_ORIGINS)
allow_credentials = bool(cors_origins) and "*" not in cors_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SlowAPIMiddleware)

app.include_router(api_router, prefix="/api/v1")
app.include_router(ws_notifications_router, prefix="/api/v1")
add_pagination(app)


@app.get("/")
async def root():
    """Health check (mặc định)."""
    return {"message": "Backend Kebook API", "docs": "/docs"}


@app.get("/kaithhealthcheck")
@app.get("/kaithheathcheck")
async def kaith_healthcheck():
    """Health check cho Leapcell."""
    return {"status": "ok"}
