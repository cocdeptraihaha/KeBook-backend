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
    OrderStatusHistoryOut,
    CheckoutRequest,
    OrderStatusUpdate,
    OrderCheckoutOut,
    CancelOrderRequest,
)
from app.services.order_service import order_service

router = APIRouter()


# ── User endpoints ──────────────────────────────────────────

@router.get("/", response_model=list[Order])
async def get_my_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status_filter: str = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Lấy đơn hàng của user, có thể lọc theo ?status=PENDING."""
    return await order_service.get_user_orders(
        db, current_user.id, skip, limit, status=status_filter
    )


@router.post("/checkout", response_model=OrderCheckoutOut, status_code=status.HTTP_201_CREATED)
async def checkout_from_cart(
    checkout_in: CheckoutRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Checkout from cart - create order from cart."""
    try:
        order, item_amount, discount_total, shipping_fee, total_amount = (
            await order_service.checkout_from_cart(db, current_user.id, checkout_in)
        )
        full_order = await order_service.get_order(db, order.id, current_user.id)
        if not full_order:
            full_order = order
        order_data = _serialize_order_with_items(full_order)
        return OrderCheckoutOut(
            order=order_data,
            item_amount=item_amount,
            discount_total=discount_total,
            shipping_fee=shipping_fee,
            total_amount=total_amount,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/", response_model=Order, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_in: OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create new order (send items manually)."""
    return await order_service.create_order(db, order_in, current_user.id)


# ── Admin endpoints (must come BEFORE /{order_id}) ──────────

@router.get("/admin/all", response_model=list[Order])
async def admin_list_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status_filter: str = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Admin: lấy tất cả đơn hàng, lọc theo ?status=…"""
    return await order_service.get_all_orders(db, skip, limit, status=status_filter)


@router.get("/admin/{order_id}", response_model=OrderWithItems)
async def admin_get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Admin: chi tiết đơn hàng bất kỳ."""
    order = await order_service.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return _serialize_order_with_items(order)


@router.patch("/admin/{order_id}/status", response_model=Order)
async def admin_update_order_status(
    order_id: int,
    body: OrderStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Admin: cập nhật trạng thái đơn."""
    order = await order_service.update_status(
        db, order_id, body.status, current_user.id, description=body.description
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found or invalid status")
    return order


# ── User order detail & actions ─────────────────────────────

@router.get("/{order_id}", response_model=OrderWithItems)
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Chi tiết đơn hàng (chỉ của chính mình), kèm timeline."""
    order = await order_service.get_order(db, order_id, current_user.id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return _serialize_order_with_items(order)


@router.post("/{order_id}/cancel", response_model=Order)
async def cancel_order(
    order_id: int,
    body: CancelOrderRequest = CancelOrderRequest(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Hủy đơn hàng hoặc gửi yêu cầu hủy."""
    try:
        order, action = await order_service.cancel_or_request_cancel(
            db, order_id, current_user.id, reason=body.reason
        )
        return order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ── helpers ─────────────────────────────────────────────────

def _serialize_order_with_items(order) -> OrderWithItems:
    """Convert ORM order to schema, mapping status_history correctly."""
    history_out = [
        OrderStatusHistoryOut.from_orm_model(h)
        for h in (order.status_history or [])
    ]
    return OrderWithItems.model_validate(
        {
            **Order.model_validate(order).model_dump(),
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
                for oi in (order.order_items or [])
            ],
            "status_history": [h.model_dump() for h in history_out],
        }
    )
