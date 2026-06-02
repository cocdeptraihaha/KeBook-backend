"""Ensure user_addresses.label exists.

Run from backend root:

  set PYTHONPATH=.
  python scripts/ensure_user_address_label_column.py
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from sqlalchemy import text

from app.core.config import get_settings
from app.core.database import engine


async def main() -> None:
    settings = get_settings()
    if "mysql" not in settings.DATABASE_URL.lower():
        print("DATABASE_URL is not MySQL; skipped.")
        return

    async with engine.begin() as conn:
        exists = await conn.execute(
            text(
                """
                SELECT COUNT(*) AS c FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = 'user_addresses'
                  AND COLUMN_NAME = 'label'
                """
            )
        )
        if int(exists.scalar() or 0) > 0:
            print("Column user_addresses.label already exists; nothing to do.")
            return

        await conn.execute(
            text("ALTER TABLE user_addresses ADD COLUMN label VARCHAR(255) DEFAULT NULL AFTER user_id")
        )
        print("Added column user_addresses.label.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
