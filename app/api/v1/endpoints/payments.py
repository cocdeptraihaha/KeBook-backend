"""Payment endpoints - SePay."""
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user
from app.core.config import get_settings
from app.core.database import get_db
from app.models.user import User
from app.models.payment import Payment, PaymentMethod
from app.models.order import Order
from app.services.sepay_service import create_payment_data

router = APIRouter()
settings = get_settings()


@router.post("/sepay/create")
async def create_sepay_payment(
    order_id: int = Query(..., description="ID đơn hàng"),
    success_url: str = Query(..., description="URL khi thanh toán thành công"),
    error_url: str = Query(..., description="URL khi thanh toán thất bại"),
    cancel_url: str = Query(..., description="URL khi user hủy"),
    payment_method: str | None = Query(None, description="CARD, BANK_TRANSFER, NAPAS_BANK_TRANSFER"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Tạo dữ liệu thanh toán SePay. Client POST form đến checkout_url."""
    from sqlalchemy import select
    from datetime import datetime

    order = await db.execute(select(Order).where(Order.id == order_id))
    order = order.scalars().first()
    if not order or order.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng")
    if order.total_price is None or order.total_price <= 0:
        raise HTTPException(status_code=400, detail="Đơn hàng không có tiền thanh toán")

    amount = int(order.total_price)
    order_invoice = f"INV_{order_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    order_description = f"Thanh toan don hang #{order_id}"

    try:
        form_data = create_payment_data(
            amount=amount,
            order_invoice_number=order_invoice,
            order_description=order_description,
            success_url=success_url,
            error_url=error_url,
            cancel_url=cancel_url,
            customer_id=str(current_user.id),
            payment_method=payment_method,
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Lưu invoice vào payment
    payment = await db.get(Payment, order.payment_id)
    if payment:
        payment.vnp_txn_ref = order_invoice  # reuse field
        payment.method = PaymentMethod.SEPAY
        await db.flush()

    return {
        "checkout_url": settings.SEPAY_CHECKOUT_URL,
        "form_data": form_data,
        "order_invoice_number": order_invoice,
    }


@router.get("/sepay/success")
@router.get("/sepay/error")
@router.get("/sepay/cancel")
async def sepay_redirect_callback(
    request: Request,
):
    """
    Callback redirect từ SePay (success/error/cancel).
    SePay redirect user về success_url/error_url/cancel_url với query params.
    Frontend nên dùng các URL này để redirect user, backend chỉ cần proxy hoặc trả JSON.
    """
    path = request.url.path
    status = "success" if "success" in path else ("error" if "error" in path else "cancel")
    params = dict(request.query_params)
    return {"status": status, "params": params}


@router.post("/sepay/ipn")
async def sepay_ipn(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    IPN - SePay gửi POST JSON khi có giao dịch.
    Header: X-Secret-Key (nếu cấu hình auth type = SECRET_KEY trong SePay).
    Cấu hình URL: https://your-domain/api/v1/payments/sepay/ipn
    Phải trả về HTTP 200 để SePay xác nhận đã nhận.
    """
    from sqlalchemy import select
    from fastapi.responses import JSONResponse
    from datetime import datetime

    # Xác thực X-Secret-Key (nếu merchant cấu hình)
    secret_key = request.headers.get("X-Secret-Key")
    if settings.SEPAY_SECRET_KEY and secret_key != settings.SEPAY_SECRET_KEY:
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized"},
        )

    try:
        body = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Invalid JSON"})

    notification_type = body.get("notification_type")
    order_data = body.get("order", {})
    transaction_data = body.get("transaction", {})
    order_invoice = order_data.get("order_invoice_number")
    transaction_id = transaction_data.get("transaction_id")
    transaction_status = transaction_data.get("transaction_status", "")
    order_status = order_data.get("order_status", "")

    if not order_invoice:
        return JSONResponse(status_code=200, content={"received": True})

    payment = await db.execute(
        select(Payment).where(Payment.vnp_txn_ref == order_invoice)
    )
    payment = payment.scalars().first()

    if not payment:
        return JSONResponse(status_code=200, content={"received": True})

    # Tránh xử lý trùng (idempotency)
    if payment.payment_status == "SUCCESS" and notification_type == "ORDER_PAID":
        return JSONResponse(status_code=200, content={"success": True, "already_processed": True})

    if notification_type == "ORDER_PAID":
        if transaction_status == "APPROVED" or order_status == "CAPTURED":
            payment.payment_status = "SUCCESS"
            payment.vnp_transaction_no = transaction_id or ""
            payment.pay_date = datetime.utcnow()
            await db.flush()

            order = await db.execute(
                select(Order).where(Order.payment_id == payment.id)
            )
            order = order.scalars().first()
            if order:
                order.status = "CONFIRMED"
                await db.flush()

    elif notification_type == "TRANSACTION_VOID":
        payment.payment_status = "VOID"
        payment.error_message = "Giao dịch đã bị hủy"
        await db.flush()

        order = await db.execute(
            select(Order).where(Order.payment_id == payment.id)
        )
        order = order.scalars().first()
        if order:
            order.status = "CANCELLED"
            await db.flush()

    return JSONResponse(status_code=200, content={"success": True})
