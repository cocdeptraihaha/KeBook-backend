"""
Thêm cột / bảng phase 3 (tracking, books SEO, promotion limits, admin_audit_log) nếu chưa có.

  cd KeBook-backend
  set PYTHONPATH=.
  python scripts/ensure_admin_phase3_columns.py
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

_root = Path(__file__).resolve().parents[1]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from sqlalchemy import text

from app.core.config import get_settings
from app.core.database import engine


async def _has_column(conn, table: str, column: str) -> bool:
    r = await conn.execute(
        text(
            """
            SELECT COUNT(*) FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :t AND COLUMN_NAME = :c
            """
        ),
        {"t": table, "c": column},
    )
    return int(r.scalar() or 0) > 0


async def _has_table(conn, table: str) -> bool:
    r = await conn.execute(
        text(
            """
            SELECT COUNT(*) FROM information_schema.TABLES
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :t
            """
        ),
        {"t": table},
    )
    return int(r.scalar() or 0) > 0


async def main() -> None:
    settings = get_settings()
    if "mysql" not in settings.DATABASE_URL.lower():
        print("DATABASE_URL không phải MySQL — bỏ qua.")
        return

    async with engine.begin() as conn:
        for table, col, ddl in [
            ("orders", "tracking_number", "ALTER TABLE orders ADD COLUMN tracking_number VARCHAR(64) NULL"),
            ("orders", "shipping_provider", "ALTER TABLE orders ADD COLUMN shipping_provider VARCHAR(64) NULL"),
            ("books", "is_published", "ALTER TABLE books ADD COLUMN is_published TINYINT(1) NOT NULL DEFAULT 1"),
            ("books", "slug", "ALTER TABLE books ADD COLUMN slug VARCHAR(255) NULL"),
            ("books", "meta_description", "ALTER TABLE books ADD COLUMN meta_description VARCHAR(255) NULL"),
            ("promotion", "min_order_amount", "ALTER TABLE promotion ADD COLUMN min_order_amount DOUBLE NULL"),
            ("promotion", "usage_limit", "ALTER TABLE promotion ADD COLUMN usage_limit INT NULL"),
            ("promotion", "used_count", "ALTER TABLE promotion ADD COLUMN used_count INT NOT NULL DEFAULT 0"),
        ]:
            if await _has_column(conn, table, col):
                print(f"Đã có {table}.{col} — bỏ qua.")
            else:
                await conn.execute(text(ddl))
                print(f"Đã thêm {table}.{col}")

        if await _has_table(conn, "admin_audit_log"):
            print("Bảng admin_audit_log đã tồn tại — bỏ qua.")
        else:
            await conn.execute(
                text(
                    """
                    CREATE TABLE admin_audit_log (
                      id INT AUTO_INCREMENT PRIMARY KEY,
                      actor_user_id INT NULL,
                      action VARCHAR(128) NOT NULL,
                      target_type VARCHAR(64) NULL,
                      target_id INT NULL,
                      payload JSON NULL,
                      ip VARCHAR(64) NULL,
                      created_at DATETIME NULL,
                      CONSTRAINT fk_admin_audit_actor FOREIGN KEY (actor_user_id) REFERENCES users(id)
                    )
                    """
                )
            )
            print("Đã tạo bảng admin_audit_log.")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
