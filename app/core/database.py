"""Database connection and session management."""
import ssl
from urllib.parse import urlparse, parse_qs, urlunparse

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings

settings = get_settings()


def _get_engine_url_and_connect_args():
    """Chuẩn hóa DATABASE_URL và trích connect_args (SSL cho MySQL Aiven)."""
    url = settings.DATABASE_URL
    connect_args = {}

    # Sửa lỗi URL dạng mysql+asyncmy://mysql://... -> mysql+asyncmy://...
    if "mysql+asyncmy://mysql://" in url:
        url = url.replace("mysql+asyncmy://mysql://", "mysql+asyncmy://")

    if "mysql" not in url:
        # SQLite: không cần xử lý gì
        return url, connect_args

    # Parse URL để xử lý SSL parameters
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    
    # Kiểm tra ssl-mode hoặc ssl_mode
    ssl_mode = query.pop("ssl-mode", query.pop("ssl_mode", [None]))[0]
    need_ssl = ssl_mode == "REQUIRED" or ssl_mode == "required"
    
    # Xóa các query params SSL khỏi URL (asyncmy không hỗ trợ trong URL)
    new_query = "&".join(f"{k}={v[0]}" for k, v in query.items() if v)
    clean_url = urlunparse(
        (parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment)
    )

    # Nếu cần SSL (Aiven MySQL), tạo SSL context
    if need_ssl:
        # Aiven MySQL dùng self-signed certificate, cần disable verification
        # Hoặc có thể tải CA cert từ Aiven và dùng: ssl.create_default_context(cafile="ca.pem")
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        connect_args["ssl"] = ssl_context

    return clean_url, connect_args


_engine_url, _connect_args = _get_engine_url_and_connect_args()
_engine_kw = {"echo": True, "future": True}

# MySQL cần pool_pre_ping và pool_recycle
if "mysql" in _engine_url:
    _engine_kw["pool_pre_ping"] = True
    _engine_kw["pool_recycle"] = 3600

# Thêm SSL connect_args nếu có
if _connect_args:
    _engine_kw["connect_args"] = _connect_args

engine = create_async_engine(_engine_url, **_engine_kw)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""
    pass


class Database:
    """Database connection manager."""

    def __init__(self):
        self.engine = engine
        self.session_factory = AsyncSessionLocal

    async def connect(self):
        """Connect to database (create tables)."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def disconnect(self):
        """Disconnect from database."""
        await self.engine.dispose()


database = Database()


async def get_db() -> AsyncSession:
    """Dependency: database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
