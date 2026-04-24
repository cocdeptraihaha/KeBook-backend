"""Order endpoints - đơn hàng."""
from datetime import date, datetime, time
from typing import Literal, Optional

import csv
import io

from fastapi import APIRouter, Depends, HTTPException, Request, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user, get_current_superuser
from app.core.database import get_db
from app.models.user import User
from app.repositories.user_repository import user_repository
from app.schemas.order import (
    Order,
    OrderCreate,
    OrderWithItems,
    OrderStatusHistoryOut,
    CheckoutRequest,
    OrderStatusUpdate,
    OrderCheckoutOut,
    CancelOrderRequest,
    CancelDecisionRequest,
    OrderMoneyStats,
    OrderRevenueStats,
    OrderShipmentUpdate,
    RevenueTimeseriesRow,
)
from app.services.audit_service import record_admin_audit
from app.services.order_service import order_service

router = APIRouter()


# ── User endpoints ──────────────────────────────────────────

@router.get("/", response_model=list[OrderWithItems])
async def get_my_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status_filter: str = Query(None, alias="status"),
    status_in: Optional[str] = Query(
        None,
        description="Nhiều trạng thái, cách nhau bởi dấu phẩy (vd. PENDING,CONFIRMED)",
    ),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Lấy đơn hàng của user; ?status= hoặc ?status_in=PENDING,CONFIRMED."""
    statuses_list = None
    if status_in and status_in.strip():
        statuses_list = [s.strip().upper() for s in status_in.split(",") if s.strip()]
    use_status = None if statuses_list else status_filter
    orders = await order_service.get_user_orders(
        db, current_user.id, skip, limit, status=use_status, statuses=statuses_list
    )
    return [
        OrderWithItems.model_validate(
            {
                **Order.model_validate(o).model_dump(),
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


@router.get("/me/stats", response_model=OrderMoneyStats)
async def get_my_order_money_stats(
    from_d: Optional[date] = Query(None, alias="from"),
    to_d: Optional[date] = Query(None, alias="to"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Thống kê tiền / số đơn theo nhóm trạng thái (theo ngày đặt hàng nếu có from/to)."""
    from_dt = datetime.combine(from_d, time.min) if from_d else None
    to_dt = datetime.combine(to_d, time.max) if to_d else None
    return await order_service.get_user_money_stats(
        db, current_user.id, from_dt=from_dt, to_dt=to_dt
    )


@router.get("/admin/stats", response_model=OrderRevenueStats)
async def admin_order_money_stats(
    from_d: Optional[date] = Query(None, alias="from"),
    to_d: Optional[date] = Query(None, alias="to"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Admin: thống kê tiền / số đơn theo nhóm trạng thái (toàn shop)."""
    from_dt = datetime.combine(from_d, time.min) if from_d else None
    to_dt = datetime.combine(to_d, time.max) if to_d else None
    stats = await order_service.get_money_stats(db, user_id=None, from_dt=from_dt, to_dt=to_dt)
    return OrderRevenueStats.model_validate(stats.model_dump())


@router.get("/admin/revenue-timeseries", response_model=list[RevenueTimeseriesRow])
async def admin_revenue_timeseries(
    from_d: Optional[date] = Query(None, alias="from"),
    to_d: Optional[date] = Query(None, alias="to"),
    group_by: Literal["day", "week", "month"] = Query("day"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Admin: chuỗi doanh thu theo ngày/tuần/tháng (đơn DELIVERED + COMPLETED)."""
    from_dt = datetime.combine(from_d, time.min) if from_d else None
    to_dt = datetime.combine(to_d, time.max) if to_d else None
    rows = await order_service.get_revenue_timeseries(
        db, from_dt=from_dt, to_dt=to_dt, group_by=group_by
    )
    return [RevenueTimeseriesRow.model_validate(r) for r in rows]


@router.post("/checkout", response_model=OrderCheckoutOut, status_code=status.HTTP_201_CREATED)
async def checkout_from_cart(
    checkout_in: CheckoutRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Checkout from cart - create order from cart."""
    try:
        (
            order,
            item_amount,
            discount_total,
            shipping_fee,
            total_amount,
            loyalty_points_redeemed,
            points_discount_amount,
        ) = await order_service.checkout_from_cart(db, current_user.id, checkout_in)
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
            loyalty_points_redeemed=loyalty_points_redeemed,
            points_discount_amount=points_discount_amount,
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

@router.get("/admin/all", response_model=list[OrderWithItems])
async def admin_list_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status_filter: str = Query(None, alias="status"),
    status_in: Optional[str] = Query(
        None,
        description="Nhiều trạng thái, cách nhau bởi dấu phẩy",
    ),
    from_d: Optional[date] = Query(None, alias="from"),
    to_d: Optional[date] = Query(None, alias="to"),
    user_id: Optional[int] = Query(None, ge=1),
    q: Optional[str] = Query(None, description="Tìm theo tên/SĐT/địa chỉ giao hàng"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Admin: lấy tất cả đơn hàng (kèm order_items), lọc status/status_in, ngày, user, tìm kiếm."""
    statuses_list = None
    if status_in and status_in.strip():
        statuses_list = [s.strip().upper() for s in status_in.split(",") if s.strip()]
    use_status = None if statuses_list else status_filter
    from_dt = datetime.combine(from_d, time.min) if from_d else None
    to_dt = datetime.combine(to_d, time.max) if to_d else None
    orders = await order_service.get_all_orders(
        db,
        skip,
        limit,
        status=use_status,
        statuses=statuses_list,
        from_dt=from_dt,
        to_dt=to_dt,
        user_id=user_id,
        q=q,
    )
    return [
        OrderWithItems.model_validate(
            {
                **Order.model_validate(o).model_dump(),
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


@router.get("/admin/export.csv")
async def admin_export_orders_csv(
    from_d: Optional[date] = Query(None, alias="from"),
    to_d: Optional[date] = Query(None, alias="to"),
    status_in: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    statuses_list = None
    if status_in and status_in.strip():
        statuses_list = [s.strip().upper() for s in status_in.split(",") if s.strip()]
    from_dt = datetime.combine(from_d, time.min) if from_d else None
    to_dt = datetime.combine(to_d, time.max) if to_d else None
    orders = await order_service.get_all_orders(
        db, 0, 5000, status=None, statuses=statuses_list, from_dt=from_dt, to_dt=to_dt
    )
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(
        [
            "id",
            "user_id",
            "user_email",
            "order_date",
            "status",
            "total_price",
            "items_count",
            "tracking_number",
        ]
    )
    for o in orders:
        u = await user_repository.get(db, o.user_id)
        email = (u.email or u.username or "") if u else ""
        w.writerow(
            [
                o.id,
                o.user_id,
                email,
                o.order_date.isoformat() if o.order_date else "",
                str(o.status or ""),
                o.total_price or 0,
                len(o.order_items or []),
                getattr(o, "tracking_number", "") or "",
            ]
        )
    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="orders_export.csv"'},
    )


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


@router.patch("/admin/{order_id}/shipment", response_model=Order)
async def admin_update_order_shipment(
    request: Request,
    order_id: int,
    body: OrderShipmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    order = await order_service.update_shipment(
        db,
        order_id,
        tracking_number=body.tracking_number,
        shipping_provider=body.shipping_provider,
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    await record_admin_audit(
        db,
        actor_user_id=current_user.id,
        action="order.shipment_update",
        target_type="order",
        target_id=order_id,
        payload=body.model_dump(exclude_unset=True),
        ip=request.client.host if request.client else None,
    )
    return order


@router.patch("/admin/{order_id}/status", response_model=Order)
async def admin_update_order_status(
    order_id: int,
    body: OrderStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Admin: cập nhật trạng thái đơn."""
    try:
        order = await order_service.update_status(
            db, order_id, body.status, current_user.id, description=body.description
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not order:
        raise HTTPException(status_code=404, detail="Order not found or invalid status")
    return order


@router.post("/admin/{order_id}/cancel-decision", response_model=Order)
async def admin_cancel_decision(
    order_id: int,
    body: CancelDecisionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Admin: chấp nhận hoặc từ chối yêu cầu hủy đơn (CANCEL_REQUESTED)."""
    try:
        order = await order_service.admin_resolve_cancel_request(
            db, order_id, body.approve, description=body.description
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
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
