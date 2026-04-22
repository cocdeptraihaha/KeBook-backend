"""Test-only endpoints - for automation testing."""
import os
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.otp import OTP
from app.models.user import User
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.order_status_history import OrderStatusHistory, OrderHistoryStatus
from app.models.payment import Payment, PaymentMethod
from app.models.service import Service
from app.models.book import Book as BookModel
from app.schemas.book import Book as BookSchema, BookCreate
from app.services.book_service import book_service

router = APIRouter()


def _is_test_env() -> bool:
    return os.getenv("TESTING") == "1" or "test.db" in os.getenv("DATABASE_URL", "")


@router.get("/otp")
async def get_otp_for_test(
    email: str,
    db: AsyncSession = Depends(get_db),
):
    """Lấy OTP mới nhất cho email (chỉ khi TESTING=1 hoặc dùng test.db)."""
    if not _is_test_env():
        return {"error": "Not available"}
    result = await db.execute(
        select(OTP).where(OTP.email == email).order_by(OTP.created_at.desc())
    )
    otp = result.scalars().first()
    return {"otp_code": otp.code if otp else None}


@router.post("/make-admin")
async def make_admin_for_test(
    email: str,
    db: AsyncSession = Depends(get_db),
):
    """Set is_superuser=True for user (only when TESTING=1)."""
    if not _is_test_env():
        return {"error": "Not available"}
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if not user:
        return {"error": "User not found"}
    user.is_superuser = True
    await db.commit()
    return {"ok": True}


@router.post("/books", response_model=BookSchema, status_code=status.HTTP_201_CREATED)
async def create_book_for_test(
    book_in: BookCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create book without token (only when TESTING=1 or test.db)."""
    if not _is_test_env():
        raise HTTPException(status_code=403, detail="Not available - use TESTING=1 or test.db")
    book = await book_service.create_book(db, book_in)
    bid = book.id
    await db.commit()
    res = await db.execute(
        select(BookModel)
        .where(BookModel.id == bid)
        .options(selectinload(BookModel.discounts))
    )
    loaded = res.scalars().first()
    if not loaded:
        raise HTTPException(status_code=500, detail="Book create failed")
    return loaded


@router.post("/seed-review-order")
async def seed_order_for_review_test(
    email: str = Query(..., description="User email (must exist)"),
    book_id: int = Query(..., ge=1),
    order_status: str = Query("DELIVERED", description="PENDING, INPROGRESS, DELIVERED, COMPLETED, ..."),
    days_since_delivery: int = Query(0, ge=0, description="DELIVERED/COMPLETED: mốc giao = bây giờ trừ N ngày"),
    db: AsyncSession = Depends(get_db),
):
    """
    Tạo đơn 1 sách (TESTING) để test review eligibility.
    Thêm lịch sử PENDING + (nếu DELIVERED/COMPLETED) bản ghi giao hàng tại mốc thời gian tương ứng.
    """
    if not _is_test_env():
        raise HTTPException(status_code=403, detail="Not available - use TESTING=1 or test.db")
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if order_status not in OrderStatus.__members__:
        raise HTTPException(status_code=400, detail=f"Invalid order_status: {order_status}")
    st = OrderStatus[order_status]

    payment = Payment(amount=0, method=PaymentMethod.COD, payment_status="PENDING")
    db.add(payment)
    await db.flush()
    sres = await db.execute(select(Service).where(Service.deleted_at.is_(None)).limit(1))
    service = sres.scalars().first()
    if not service:
        service = Service(name_service="Test", price=0, status=True)
        db.add(service)
        await db.flush()

    now = datetime.now(timezone.utc)
    # naive cho DB nếu cột không có tz (đồng bộ với phần còn lại dùng utc)
    n = now.replace(tzinfo=None)

    order = Order(
        user_id=user.id,
        payment_id=payment.id,
        service_id=service.id,
        full_name="Seed",
        phone_number="0900000000",
        shipping_address="Test addr",
        status=st,
        total_price=10.0,
        order_date=n,
    )
    db.add(order)
    await db.flush()
    oi = OrderItem(
        order_id=order.id,
        book_id=book_id,
        quantity=1,
        price=10.0,
        book_title="Seed book",
    )
    db.add(oi)

    p_hist = OrderStatusHistory(
        order_id=order.id,
        e_order_history=OrderHistoryStatus.PENDING,
        status_change_date=n,
        description="seed",
    )
    db.add(p_hist)

    if st in (OrderStatus.DELIVERED, OrderStatus.COMPLETED):
        at = n - timedelta(days=days_since_delivery)
        d_hist = OrderStatusHistory(
            order_id=order.id,
            e_order_history=OrderHistoryStatus.DELIVERED
            if st == OrderStatus.DELIVERED
            else OrderHistoryStatus.COMPLETED,
            status_change_date=at,
            description="seed delivery",
        )
        db.add(d_hist)

    await db.commit()
    return {"ok": True, "order_id": order.id, "user_id": user.id}
