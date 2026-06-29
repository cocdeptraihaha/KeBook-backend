"""Order endpoints - đơn hàng."""
from datetime import date, datetime, time
from typing import Literal, Optional

import csv
import io

from fastapi import APIRouter, Depends, HTTPException, Request, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import apaginate

from app.api.dependencies import get_current_active_user, get_current_superuser
from app.core.database import get_db
from app.core.ratelimit import limiter
from app.models.book import Book
from app.models.book_detail import BookDetail
from app.models.book_image import BookImage
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

@router.get("/", response_model=Page[OrderWithItems])
async def get_my_orders(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
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

    from sqlalchemy.orm import selectinload
    from sqlalchemy import func
    import math
    from app.models.order import Order as OrderModel, OrderStatus

    stmt = (
        select(OrderModel)
        .where(
            OrderModel.user_id == current_user.id,
            OrderModel.deleted_at.is_(None),
        )
        .options(selectinload(OrderModel.order_items))
    )
    if statuses_list:
        enums = []
        for s in statuses_list:
            key = (s or "").strip().upper()
            if key in OrderStatus.__members__:
                enums.append(OrderStatus[key])
        if enums:
            stmt = stmt.where(OrderModel.status.in_(enums))
    elif use_status:
        stmt = stmt.where(OrderModel.status == use_status)

    stmt = stmt.order_by(OrderModel.order_date.desc())

    # Count total items manually using subquery to be database agnostic and robust
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = await db.scalar(count_stmt) or 0

    # Paginate using limit and offset on db query
    stmt = stmt.limit(size).offset((page - 1) * size)
    res = await db.execute(stmt)
    orders_list = res.scalars().all()

    new_items = []
    for o in orders_list:
        await order_service.auto_confirm_if_needed(db, o)
        payment_method, payment_status = await _get_payment_info(db, o)
        direct_payment_status = None
        if getattr(o, "payment_status", None):
            if hasattr(o.payment_status, "value"):
                direct_payment_status = o.payment_status.value
            else:
                direct_payment_status = str(o.payment_status)
        new_items.append(
            OrderWithItems.model_validate(
                {
                    **Order.model_validate(o).model_dump(),
                    "payment_method": payment_method,
                    "payment_status": direct_payment_status or "UNPAID",
                    "transaction_status": payment_status,
                    "order_items": await _build_order_items_payload(
                        db, o.order_items or []
                    ),
                    "status_history": [],
                }
            )
        )

    pages = math.ceil(total / size) if size > 0 else 0
    return Page(items=new_items, total=total, page=page, size=size, pages=pages)


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
    group_by: Literal["day", "week", "month", "quarter"] = Query("day"),
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
    request: Request,
    checkout_in: CheckoutRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Checkout from cart - create order from cart."""
    import os
    from datetime import timedelta
    from app.models.order import Order as OrderModel
    from sqlalchemy import desc

    if os.environ.get("TESTING") != "1":
        latest_order_res = await db.execute(
            select(OrderModel)
            .where(OrderModel.user_id == current_user.id)
            .order_by(desc(OrderModel.order_date))
            .limit(1)
        )
        latest_order = latest_order_res.scalars().first()
        if latest_order:
            delta = datetime.utcnow() - latest_order.order_date
            if delta < timedelta(seconds=30):
                raise HTTPException(
                    status_code=400,
                    detail="Thao tác quá nhanh. Vui lòng đợi 30 giây giữa các lần đặt hàng."
                )

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
        order_data = await _serialize_order_with_items(db, full_order)

        payment_url = None
        method_str = (checkout_in.payment_method or "COD").upper()
        if method_str == "VNPAY":
            from app.services.vnpay_service import vnpay_service
            client_ip = request.client.host if request.client else "127.0.0.1"
            payment_url = vnpay_service.generate_payment_url(
                order_id=order.id,
                amount=total_amount,
                ip_address=client_ip,
                order_info=f"Thanh toan don hang #{order.id} tai KeBook"
            )

        return OrderCheckoutOut(
            order=order_data,
            item_amount=item_amount,
            discount_total=discount_total,
            shipping_fee=shipping_fee,
            total_amount=total_amount,
            loyalty_points_redeemed=loyalty_points_redeemed,
            points_discount_amount=points_discount_amount,
            payment_url=payment_url,
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

@router.get("/admin/all", response_model=Page[OrderWithItems])
async def admin_list_orders(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
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

    from sqlalchemy.orm import selectinload
    from sqlalchemy import or_, func
    import math
    from app.models.order import Order as OrderModel, OrderStatus

    stmt = (
        select(OrderModel)
        .where(OrderModel.deleted_at.is_(None))
        .options(selectinload(OrderModel.order_items))
    )
    if statuses_list:
        enums = []
        for s in statuses_list:
            key = (s or "").strip().upper()
            if key in OrderStatus.__members__:
                enums.append(OrderStatus[key])
        if enums:
            stmt = stmt.where(OrderModel.status.in_(enums))
    elif use_status:
        key = (use_status or "").strip().upper()
        if key in OrderStatus.__members__:
            stmt = stmt.where(OrderModel.status == OrderStatus[key])
        else:
            stmt = stmt.where(OrderModel.status == use_status)
    if from_dt is not None:
        stmt = stmt.where(OrderModel.order_date >= from_dt)
    if to_dt is not None:
        stmt = stmt.where(OrderModel.order_date <= to_dt)
    if user_id is not None:
        stmt = stmt.where(OrderModel.user_id == user_id)
    if q and q.strip():
        term = f"%{q.strip()}%"
        stmt = stmt.where(
            or_(
                OrderModel.full_name.like(term),
                OrderModel.phone_number.like(term),
                OrderModel.shipping_address.like(term),
            )
        )
    stmt = stmt.order_by(OrderModel.order_date.desc())

    # Count total items manually using subquery to be database agnostic and robust
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = await db.scalar(count_stmt) or 0

    # Paginate using limit and offset on db query
    stmt = stmt.limit(size).offset((page - 1) * size)
    res = await db.execute(stmt)
    orders_list = res.scalars().all()

    new_items = []
    for o in orders_list:
        payment_method, payment_status = await _get_payment_info(db, o)
        direct_payment_status = None
        if getattr(o, "payment_status", None):
            if hasattr(o.payment_status, "value"):
                direct_payment_status = o.payment_status.value
            else:
                direct_payment_status = str(o.payment_status)
        new_items.append(
            OrderWithItems.model_validate(
                {
                    **Order.model_validate(o).model_dump(),
                    "payment_method": payment_method,
                    "payment_status": direct_payment_status or "UNPAID",
                    "transaction_status": payment_status,
                    "order_items": await _build_order_items_payload(
                        db, o.order_items or []
                    ),
                    "status_history": [],
                }
            )
        )

    pages = math.ceil(total / size) if size > 0 else 0
    return Page(items=new_items, total=total, page=page, size=size, pages=pages)


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
    return await _serialize_order_with_items(db, order)


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
    return await _serialize_order_with_items(db, order)


@router.post("/{order_id}/payment-url")
async def get_order_payment_url(
    request: Request,
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Lấy link thanh toán VNPAY cho một đơn hàng cụ thể."""
    order = await order_service.get_order(db, order_id, current_user.id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    from app.services.vnpay_service import vnpay_service
    client_ip = request.client.host if request.client else "127.0.0.1"
    url = vnpay_service.generate_payment_url(
        order_id=order.id,
        amount=order.total_price or 0.0,
        ip_address=client_ip,
        order_info=f"Thanh toan don hang #{order.id} tai KeBook"
    )
    return {"payment_url": url}


@router.get("/payment/vnpay-callback")
async def vnpay_callback(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """VNPay Callback / IPN receiver endpoint to process payment status securely."""
    from app.services.vnpay_service import vnpay_service
    from app.models.payment import Payment
    from sqlalchemy import select

    params = dict(request.query_params)
    is_valid = vnpay_service.verify_signature(params)
    if not is_valid:
        # VNPay IPN requires RspCode 97 for invalid signature
        return {"RspCode": "97", "Message": "Invalid Signature"}

    vnp_txn_ref = params.get("vnp_TxnRef", "")
    vnp_response_code = params.get("vnp_ResponseCode", "")
    vnp_transaction_no = params.get("vnp_TransactionNo", "")
    vnp_amount_str = params.get("vnp_Amount", "0")

    # vnp_TxnRef is formatted as {order_id}_{create_date}
    if "_" in vnp_txn_ref:
        order_id_str = vnp_txn_ref.split("_")[0]
    else:
        order_id_str = vnp_txn_ref

    try:
        order_id = int(order_id_str)
    except ValueError:
        return {"RspCode": "01", "Message": "Order not found"}

    # Fetch order and lock row to prevent race conditions (Race Condition / Concurrent writes)
    from app.models.order import Order
    order_res = await db.execute(
        select(Order)
        .where(Order.id == order_id)
        .with_for_update()
    )
    order = order_res.scalars().first()
    if not order:
        return {"RspCode": "01", "Message": "Order not found"}

    # Fetch and lock associated payment record
    payment_res = await db.execute(
        select(Payment)
        .where(Payment.id == order.payment_id)
        .with_for_update()
    )
    payment = payment_res.scalars().first()
    if not payment:
        return {"RspCode": "01", "Message": "Order not found"}

    # Check Idempotency (Already confirmed)
    if payment.payment_status in ("SUCCESS", "FAILED", "AMOUNT_MISMATCH", "SUCCESS_MANUAL_REVIEW"):
        return {
            "RspCode": "02",
            "Message": "Order already confirmed",
            "status": "SUCCESS" if payment.payment_status in ("SUCCESS", "SUCCESS_MANUAL_REVIEW") else "FAILED",
            "order_id": order_id,
        }

    # Verify Amount (Amount mismatch verification)
    try:
        vnp_amount = float(vnp_amount_str) / 100.0
    except ValueError:
        vnp_amount = 0.0

    order_amount = float(order.total_price or 0.0)
    if abs(vnp_amount - order_amount) > 0.01:
        payment.payment_status = "AMOUNT_MISMATCH"
        payment.vnp_transaction_no = vnp_transaction_no
        payment.vnp_txn_ref = vnp_txn_ref
        payment.error_message = f"Amount mismatch. Received {vnp_amount}, expected {order_amount}"
        await db.commit()
        return {"RspCode": "04", "Message": "Invalid Amount"}

    payment.vnp_transaction_no = vnp_transaction_no
    payment.vnp_txn_ref = vnp_txn_ref

    from datetime import datetime
    payment.pay_date = datetime.utcnow()

    # Process status
    if vnp_response_code == "00":
        # Handle Late Webhook vs Cancelled Order
        if order.status == "CANCELLED":
            payment.payment_status = "SUCCESS_MANUAL_REVIEW"
            payment.error_message = "Payment successful but order was already cancelled. Manual refund needed."
            order_service._add_history(
                db,
                order.id,
                "CANCELLED",
                f"Thanh toan online VNPAY thanh cong {vnp_amount}đ nhung don da bi huy truoc do. Can review hoan tien thu cong."
            )
        else:
            payment.payment_status = "SUCCESS"
            order.status = "CONFIRMED"
            from app.models.order import OrderPaymentStatus
            order.payment_status = OrderPaymentStatus.PAID
            order_service._add_history(
                db,
                order.id,
                "CONFIRMED",
                f"Thanh toan online VNPAY thanh cong. Ma giao dich: {vnp_transaction_no}"
            )
    else:
        payment.payment_status = "FAILED"
        payment.error_message = f"VNPAY response code: {vnp_response_code}"
        # Only log history if order is not already cancelled
        if order.status != "CANCELLED":
            order_service._add_history(
                db,
                order.id,
                "PENDING",
                f"Thanh toan online VNPAY that bai. Response code: {vnp_response_code}"
            )

    await db.commit()
    return {
        "RspCode": "00",
        "Message": "Confirm Success",
        "status": "SUCCESS" if payment.payment_status in ("SUCCESS", "SUCCESS_MANUAL_REVIEW") else "FAILED",
        "order_id": order_id,
        "message": "Payment processed successfully"
    }


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


@router.post("/{order_id}/confirm-received", response_model=Order)
async def confirm_received_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Xác nhận đã nhận hàng - cập nhật sang COMPLETED."""
    order = await order_service.get_order(db, order_id, current_user.id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    try:
        # Update order status to COMPLETED
        updated_order = await order_service.update_status(
            db, order_id, "COMPLETED", description="Khách hàng xác nhận đã nhận hàng"
        )
        return updated_order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))



# ── helpers ─────────────────────────────────────────────────

async def _get_payment_info(db: AsyncSession, order) -> tuple[Optional[str], Optional[str]]:
    payment_method = None
    payment_status = None
    if "payment" in order.__dict__ and order.payment is not None:
        payment_method = order.payment.method.value if order.payment.method else None
        payment_status = order.payment.payment_status
    elif getattr(order, "payment_id", None):
        from app.models.payment import Payment
        payment_res = await db.execute(select(Payment).where(Payment.id == order.payment_id))
        pay = payment_res.scalars().first()
        if pay:
            payment_method = pay.method.value if pay.method else None
            payment_status = pay.payment_status
    return payment_method, payment_status


async def _serialize_order_with_items(db: AsyncSession, order) -> OrderWithItems:
    """Convert ORM order to schema, mapping status_history correctly."""
    history_out = [
        OrderStatusHistoryOut.from_orm_model(h)
        for h in (order.status_history or [])
    ]
    payment_method, payment_status = await _get_payment_info(db, order)

    # Load shipping fee from service price
    shipping_fee = 0.0
    if "service" in order.__dict__ and order.service is not None:
        shipping_fee = float(order.service.price or 0.0)
    elif getattr(order, "service_id", None):
        from app.models.service import Service
        srv_res = await db.execute(select(Service).where(Service.id == order.service_id))
        srv = srv_res.scalars().first()
        if srv:
            shipping_fee = float(srv.price or 0.0)

    # Load voucher discount from order_promotion
    discount_amount = 0.0
    from app.models.order_promotion import OrderPromotion
    promo_res = await db.execute(select(OrderPromotion).where(OrderPromotion.order_id == order.id))
    promos = promo_res.scalars().all()
    discount_amount = sum(float(p.discount_amount or 0.0) for p in promos)

    # Load loyalty points discount from point_transactions
    points_discount = 0.0
    from app.models.point_transaction import PointTransaction
    from app.core.config import get_settings
    pts_res = await db.execute(
        select(PointTransaction).where(
            PointTransaction.ref_type == "order",
            PointTransaction.ref_id == order.id,
            PointTransaction.delta < 0
        )
    )
    pts_tx = pts_res.scalars().first()
    if pts_tx:
        settings = get_settings()
        point_val = max(0.0001, float(settings.LOYALTY_POINT_VALUE_VND or 1.0))
        points_discount = abs(pts_tx.delta) * point_val

    # Retrieve order level payment status
    direct_payment_status = None
    if getattr(order, "payment_status", None):
        if hasattr(order.payment_status, "value"):
            direct_payment_status = order.payment_status.value
        else:
            direct_payment_status = str(order.payment_status)

    return OrderWithItems.model_validate(
        {
            **Order.model_validate(order).model_dump(),
            "payment_method": payment_method,
            "payment_status": direct_payment_status or "UNPAID",
            "transaction_status": payment_status,
            "order_items": await _build_order_items_payload(
                db, order.order_items or []
            ),
            "status_history": [h.model_dump() for h in history_out],
            "shipping_fee": shipping_fee,
            "discount_amount": discount_amount,
            "points_discount": points_discount,
        }
    )


async def _build_order_items_payload(db: AsyncSession, order_items) -> list[dict]:
    book_ids = sorted({oi.book_id for oi in order_items if oi.book_id is not None})
    image_map: dict[int, str | None] = {}
    if book_ids:
        result = await db.execute(
            select(BookImage.book_id, BookImage.image_url)
            .where(BookImage.book_id.in_(book_ids))
            .order_by(BookImage.book_id, BookImage.is_primary.desc(), BookImage.sort_order)
        )
        for book_id, image_url in result.all():
            if int(book_id) not in image_map:
                image_map[int(book_id)] = image_url

    out: list[dict] = []
    for oi in order_items:
        out.append(
            {
                "id": oi.id,
                "order_id": oi.order_id,
                "book_id": oi.book_id,
                "book_title": oi.book_title,
                "image_url": image_map.get(int(oi.book_id)) if oi.book_id else None,
                "quantity": oi.quantity,
                "price": float(oi.price or 0),
                "deleted_at": oi.deleted_at,
            }
        )
    return out
