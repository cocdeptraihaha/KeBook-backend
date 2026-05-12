"""Database connection and session management."""
import ssl
from urllib.parse import parse_qs, urlparse, urlunparse

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings

settings = get_settings()


def _get_engine_url_and_connect_args():
    """Normalize DATABASE_URL and build connect_args (MySQL SSL support)."""
    url = settings.DATABASE_URL
    connect_args = {}

    if "mysql+aiomysql://mysql://" in url:
        url = url.replace("mysql+aiomysql://mysql://", "mysql+aiomysql://")

    if "mysql" not in url:
        return url, connect_args

    parsed = urlparse(url)
    query = parse_qs(parsed.query)

    ssl_mode = query.pop("ssl-mode", query.pop("ssl_mode", [None]))[0]
    need_ssl = ssl_mode in {"REQUIRED", "required"}

    new_query = "&".join(f"{k}={v[0]}" for k, v in query.items() if v)
    clean_url = urlunparse(
        (parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment)
    )

    if need_ssl:
        ssl_ca = (settings.MYSQL_SSL_CA or "").strip() or None
        ssl_context = ssl.create_default_context(cafile=ssl_ca)
        if settings.MYSQL_SSL_VERIFY:
            ssl_context.check_hostname = True
            ssl_context.verify_mode = ssl.CERT_REQUIRED
        else:
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
        connect_args["ssl"] = ssl_context

    return clean_url, connect_args


_engine_url, _connect_args = _get_engine_url_and_connect_args()
_engine_kw = {"echo": True, "future": True}

if "mysql" in _engine_url:
    _engine_kw["pool_pre_ping"] = True
    _engine_kw["pool_recycle"] = 3600

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


class Database:
    """Database connection manager."""

    def __init__(self):
        self.engine = engine
        self.session_factory = AsyncSessionLocal

    async def connect(self):
        """Connect to database (create tables)."""
        import app.models  # noqa: F401 - register all models with Base.metadata

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
