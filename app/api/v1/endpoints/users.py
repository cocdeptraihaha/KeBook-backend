"""User endpoints."""
import csv
import io
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import (
    get_current_active_user,
    get_current_superuser,
    get_current_user,
)
from app.core.database import get_db
from app.models.book import Book
from app.models.book_view import BookView
from app.models.promotion import Promotion
from app.models.user import User
from app.models.user_promotion import UserPromotion
from app.schemas.book import Book as BookSchema
from app.schemas.point_transaction import LoyaltyBalanceOut, PointTransactionOut
from app.schemas.order import Order as OrderSchema, OrderWithItems
from app.schemas.user import (
    AdminPointsAdjustBody,
    AdminUserRoleBody,
    AdminUserStatusBody,
    User as UserSchema,
    UserUpdate,
)
from app.repositories.point_transaction_repository import point_transaction_repository
from app.services.audit_service import record_admin_audit
from app.services.order_service import order_service
from app.services.points_service import points_service
from app.services.user_service import user_service

router = APIRouter()


# ── Admin (đăng ký trước /{user_id}) ─────────────────────────

@router.get("/admin/all", response_model=list[UserSchema])
async def admin_list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    q: str | None = Query(None),
    is_active: bool | None = Query(None),
    is_superuser: bool | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    return await user_service.repository.list_admin(
        db,
        skip=skip,
        limit=limit,
        q=q,
        is_active=is_active,
        is_superuser=is_superuser,
    )


@router.patch("/admin/{user_id}/status", response_model=UserSchema)
async def admin_set_user_active(
    request: Request,
    user_id: int,
    body: AdminUserStatusBody,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    user = await user_service.repository.get(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = body.is_active
    await db.flush()
    await db.refresh(user)
    await record_admin_audit(
        db,
        actor_user_id=current_user.id,
        action="user.set_active",
        target_type="user",
        target_id=user_id,
        payload={"is_active": body.is_active},
        ip=request.client.host if request.client else None,
    )
    return user


@router.patch("/admin/{user_id}/role", response_model=UserSchema)
async def admin_set_user_role(
    user_id: int,
    body: AdminUserRoleBody,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    user = await user_service.repository.get(db, user_id)
    if not user or user.deleted_at is not None:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_superuser = body.is_superuser
    await db.flush()
    await db.refresh(user)
    return user


@router.post("/admin/{user_id}/points-adjust", response_model=LoyaltyBalanceOut)
async def admin_adjust_user_points(
    user_id: int,
    body: AdminPointsAdjustBody,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    user = await user_service.repository.get(db, user_id)
    if not user or user.deleted_at is not None:
        raise HTTPException(status_code=404, detail="User not found")
    try:
        bal = await points_service.adjust_points(
            db, user_id, body.delta, reason=body.reason or points_service.REASON_ADMIN
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return LoyaltyBalanceOut(balance=bal)


@router.get("/admin/export.csv")
async def admin_export_users_csv(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    rows = await user_service.repository.list_admin(db, skip=0, limit=10000)
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(
        ["id", "email", "username", "full_name", "is_active", "is_superuser", "loyalty_points"]
    )
    for u in rows:
        w.writerow(
            [
                u.id,
                u.email or "",
                u.username or "",
                u.full_name or "",
                u.is_active,
                u.is_superuser,
                getattr(u, "loyalty_points", 0) or 0,
            ]
        )
    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="users_export.csv"'},
    )


@router.get("/admin/{user_id}/orders", response_model=list[OrderWithItems])
async def admin_list_user_orders(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    user = await user_service.repository.get(db, user_id)
    if not user or user.deleted_at is not None:
        raise HTTPException(status_code=404, detail="User not found")
    orders = await order_service.get_user_orders(db, user_id, skip, limit)
    return [
        OrderWithItems.model_validate(
            {
                **OrderSchema.model_validate(o).model_dump(),
                "order_items": [
                    {
                        "id": oi.id,
                        "order_id": oi.order_id,
                        "book_id": oi.book_id,
                        "book_title": oi.book_title,
                        "quantity": oi.quantity,
                        "price": float(oi.price or 0),
                        "deleted_at": oi.deleted_at,
                    }
                    for oi in (o.order_items or [])
                ],
                "status_history": [],
            }
        )
        for o in orders
    ]


@router.get("/me", response_model=UserSchema)
async def read_current_user(current_user: User = Depends(get_current_user)):
    """Get logged-in user info."""
    return current_user


@router.get("/me/points", response_model=LoyaltyBalanceOut)
async def read_my_loyalty_points(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    bal = await points_service.get_balance(db, current_user.id)
    return LoyaltyBalanceOut(balance=bal)


@router.get("/me/point-transactions", response_model=list[PointTransactionOut])
async def read_my_point_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    rows = await point_transaction_repository.list_by_user(
        db, current_user.id, skip=skip, limit=limit
    )
    return rows


@router.get("/me/viewed", response_model=list[BookSchema])
async def read_my_recently_viewed(
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Sách đã xem gần đây (distinct theo book_id, mới nhất trước)."""
    subq = (
        select(BookView.book_id, func.max(BookView.viewed_at).label("last_at"))
        .where(BookView.user_id == current_user.id)
        .group_by(BookView.book_id)
        .subquery()
    )
    r = await db.execute(
        select(Book)
        .join(subq, Book.id == subq.c.book_id)
        .where(Book.deleted_at.is_(None))
        .order_by(subq.c.last_at.desc())
        .limit(limit)
    )
    return list(r.scalars().all())


@router.get("/me/promotions", response_model=list[dict])
async def read_my_owned_promotions(
    unused_only: bool = Query(False, description="Chỉ mã còn dùng được (chưa gắn đơn)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Mã giảm giá cá nhân (đổi điểm): promotion.owner_user_id = tôi."""
    now = datetime.utcnow()
    stmt = select(Promotion).where(
        Promotion.owner_user_id == current_user.id,
        Promotion.deleted_at.is_(None),
        or_(Promotion.start_date.is_(None), Promotion.start_date <= now),
        or_(Promotion.end_date.is_(None), Promotion.end_date >= now),
    )
    r = await db.execute(stmt)
    promos = list(r.scalars().all())
    out: list[dict] = []
    for p in promos:
        used_r = await db.execute(
            select(UserPromotion).where(
                and_(
                    UserPromotion.user_id == current_user.id,
                    UserPromotion.promotion_id == p.id,
                    UserPromotion.order_id.is_not(None),
                )
            )
        )
        used = used_r.scalars().first() is not None
        if unused_only and used:
            continue
        out.append(
            {
                "id": p.id,
                "code": p.code,
                "name": p.name,
                "discount_percent": p.discount_percent,
                "max_discount": p.max_discount,
                "start_date": p.start_date,
                "end_date": p.end_date,
                "used": used,
            }
        )
    return out


@router.get("/{user_id}", response_model=UserSchema)
async def read_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user by ID (self or admin only)."""
    if current_user.id != user_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Permission denied")
    user = await user_service.repository.get(db, user_id)
    if not user or user.deleted_at is not None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update user (own profile only)."""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Permission denied")
    user = await user_service.update_user(db, user_id, user_in)
    if not user or user.deleted_at is not None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Soft delete user (own account only)."""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Permission denied")

    user = await user_service.repository.get(db, user_id)
    if not user or user.deleted_at is not None:
        raise HTTPException(status_code=404, detail="User not found")

    user.deleted_at = datetime.utcnow()
    await db.flush()
