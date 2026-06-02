"""User address book service."""
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.user_address import UserAddress
from app.schemas.address import UserAddressCreate, UserAddressUpdate


class UserAddressService:
    """Business logic for user address book."""

    async def list_for_user(self, db: AsyncSession, user_id: int) -> list[UserAddress]:
        result = await db.execute(
            select(UserAddress)
            .where(UserAddress.user_id == user_id, UserAddress.deleted_at.is_(None))
            .order_by(UserAddress.is_default.desc(), UserAddress.id.desc())
        )
        return list(result.scalars().all())

    async def get_for_user(
        self, db: AsyncSession, user_id: int, address_id: int
    ) -> Optional[UserAddress]:
        result = await db.execute(
            select(UserAddress).where(
                UserAddress.id == address_id,
                UserAddress.user_id == user_id,
                UserAddress.deleted_at.is_(None),
            )
        )
        return result.scalars().first()

    async def create_for_user(
        self,
        db: AsyncSession,
        user: User,
        address_in: UserAddressCreate,
    ) -> UserAddress:
        rows = await self.list_for_user(db, user.id)
        is_default = bool(address_in.is_default) or not rows
        if is_default:
            await self._clear_default(db, user.id)

        address = UserAddress(
            user_id=user.id,
            label=address_in.label,
            recipient_name=address_in.recipient_name or user.full_name,
            phone_number=address_in.phone_number or user.phone_number,
            address_detail=address_in.address_detail,
            ward=address_in.ward,
            province=address_in.province,
            is_default=is_default,
        )
        db.add(address)
        await db.flush()
        await db.refresh(address)
        return address

    async def update_for_user(
        self,
        db: AsyncSession,
        user_id: int,
        address_id: int,
        address_in: UserAddressUpdate,
    ) -> Optional[UserAddress]:
        address = await self.get_for_user(db, user_id, address_id)
        if not address:
            return None

        data = address_in.model_dump(exclude_unset=True)
        if data.get("is_default") is True:
            await self._clear_default(db, user_id, except_id=address_id)
        for key, value in data.items():
            setattr(address, key, value)
        address.updated_at = datetime.utcnow()
        await db.flush()
        await db.refresh(address)
        return address

    async def set_default(
        self, db: AsyncSession, user_id: int, address_id: int
    ) -> Optional[UserAddress]:
        address = await self.get_for_user(db, user_id, address_id)
        if not address:
            return None
        await self._clear_default(db, user_id, except_id=address_id)
        address.is_default = True
        address.updated_at = datetime.utcnow()
        await db.flush()
        await db.refresh(address)
        return address

    async def soft_delete(self, db: AsyncSession, user_id: int, address_id: int) -> bool:
        address = await self.get_for_user(db, user_id, address_id)
        if not address:
            return False
        was_default = bool(address.is_default)
        address.deleted_at = datetime.utcnow()
        address.is_default = False
        address.updated_at = datetime.utcnow()
        await db.flush()

        if was_default:
            rows = await self.list_for_user(db, user_id)
            if rows:
                rows[0].is_default = True
                rows[0].updated_at = datetime.utcnow()
                await db.flush()
        return True

    async def _clear_default(
        self, db: AsyncSession, user_id: int, except_id: Optional[int] = None
    ) -> None:
        rows = await self.list_for_user(db, user_id)
        for row in rows:
            if except_id is not None and row.id == except_id:
                continue
            row.is_default = False
            row.updated_at = datetime.utcnow()
        await db.flush()


user_address_service = UserAddressService()
