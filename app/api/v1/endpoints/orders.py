"""Order endpoints - đơn hàng."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user, get_current_superuser
from app.core.database import get_db
from app.models.user import User
from app.schemas.order import (
    Order,
    OrderCreate,
    OrderWithItems,
    CheckoutRequest,
    OrderStatusUpdate,
    OrderCheckoutOut,
)
from app.services.order_service import order_service

router = APIRouter()


@router.get("/", response_model=list[Order])
async def get_my_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get orders of logged-in user."""
    return await order_service.get_user_orders(db, current_user.id, skip, limit)


@router.get("/{order_id}", response_model=OrderWithItems)
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Chi tiết đơn hàng (chỉ của chính mình)."""
    order = await order_service.get_order(db, order_id, current_user.id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.post("/checkout", response_model=OrderCheckoutOut, status_code=status.HTTP_201_CREATED)
async def checkout_from_cart(
    checkout_in: CheckoutRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Checkout from cart - create order from cart. Tính toàn bộ tiền ở backend."""
    try:
        order, item_amount, discount_total, shipping_fee, total_amount = await order_service.checkout_from_cart(
            db, current_user.id, checkout_in
        )
        # Lấy lại order kèm items để trả về đầy đủ
        full_order = await order_service.get_order(db, order.id, current_user.id)
        if not full_order:
            full_order = order
        return OrderCheckoutOut(
            order=full_order,  # type: ignore[arg-type]
            item_amount=item_amount,
            discount_total=discount_total,
            shipping_fee=shipping_fee,
            total_amount=total_amount,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{order_id}/status", response_model=Order)
async def update_order_status(
    order_id: int,
    body: OrderStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Update order status (admin)."""
    order = await order_service.update_status(
        db, order_id, body.status, current_user.id
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.post("/", response_model=Order, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_in: OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create new order (send items manually)."""
    return await order_service.create_order(db, order_in, current_user.id)
