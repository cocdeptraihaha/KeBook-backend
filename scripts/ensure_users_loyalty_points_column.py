"""
Thêm cột users.loyalty_points nếu DB MySQL chưa có (khớp model SQLAlchemy).

Chạy từ thư mục gốc backend (cùng môi trường với uvicorn):

  cd KeBook-backend
  set PYTHONPATH=.
  python scripts/ensure_users_loyalty_points_column.py

Hoặc chạy SQL trực tiếp trên MySQL (Aiven / local):

  ALTER TABLE users ADD COLUMN loyalty_points INT NOT NULL DEFAULT 0;

(Nếu báo duplicate column thì đã có cột — bỏ qua.)
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Cho phép `python scripts/...py` từ thư mục gốc repo
_root = Path(__file__).resolve().parents[1]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from sqlalchemy import text

from app.core.config import get_settings
from app.core.database import engine


async def main() -> None:
    settings = get_settings()
    if "mysql" not in settings.DATABASE_URL.lower():
        print("DATABASE_URL không phải MySQL — bỏ qua.")
        return

    async with engine.begin() as conn:
        r = await conn.execute(
            text(
                """
                SELECT COUNT(*) AS c FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = 'users'
                  AND COLUMN_NAME = 'loyalty_points'
                """
            )
        )
        n = int(r.scalar() or 0)
        if n > 0:
            print("Cột users.loyalty_points đã tồn tại — không làm gì.")
            return
        await conn.execute(
            text(
                "ALTER TABLE users ADD COLUMN loyalty_points INT NOT NULL DEFAULT 0"
            )
        )
        print("Đã thêm cột users.loyalty_points INT NOT NULL DEFAULT 0.")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
