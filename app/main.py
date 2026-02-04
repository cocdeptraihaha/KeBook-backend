"""Application entry point."""
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.api.v1.router import api_router
from app.core.database import database, AsyncSessionLocal
from app.services.otp_service import otp_service

# Chu kỳ xóa OTP hết hạn (giây)
OTP_CLEANUP_INTERVAL = 60


async def _periodic_otp_cleanup(stopped: asyncio.Event):
    """Chạy nền: định kỳ xóa OTP hết hạn và user chưa kích hoạt có OTP hết hạn."""
    while not stopped.is_set():
        try:
            async with AsyncSessionLocal() as session:
                users_n, otps_n = await otp_service.cleanup_expired_otps_and_inactive_users(session)
                await session.commit()
                if users_n > 0 or otps_n > 0:
                    if users_n > 0:
                        print(f"[OTP] Đã xóa {users_n} user chưa kích hoạt (OTP hết hạn).")
                    if otps_n > 0:
                        print(f"[OTP] Đã xóa {otps_n} mã OTP hết hạn.")
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"[OTP] Lỗi khi dọn OTP/user hết hạn: {e}")
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Health check (mặc định)."""
    return {"message": "Backend Kebook API", "docs": "/docs"}


@app.get("/kaithhealthcheck")
@app.get("/kaithheathcheck")
async def kaith_healthcheck():
    """Health check cho Leapcell."""
    return {"status": "ok"}
