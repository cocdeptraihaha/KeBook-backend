"""SePay payment service."""
import base64
import hmac
import hashlib
from typing import Optional

from app.core.config import get_settings

settings = get_settings()

SIGNED_FIELDS = [
    "merchant",
    "operation",
    "payment_method",
    "order_amount",
    "currency",
    "order_invoice_number",
    "order_description",
    "customer_id",
    "success_url",
    "error_url",
    "cancel_url",
]


def _make_sepay_signature(fields: dict, secret: str) -> str:
    """Tạo chữ ký HMAC-SHA256 base64 cho SePay."""
    signed_parts = []
    for field in SIGNED_FIELDS:
        if field in fields and fields[field]:
            signed_parts.append(f"{field}={fields[field]}")
    signed_string = ",".join(signed_parts)
    sig = hmac.new(
        secret.encode("utf-8"),
        signed_string.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    return base64.b64encode(sig).decode("utf-8")


def create_payment_data(
    amount: int,
    order_invoice_number: str,
    order_description: str,
    success_url: str,
    error_url: str,
    cancel_url: str,
    customer_id: Optional[str] = None,
    payment_method: Optional[str] = None,
) -> dict:
    """
    Tạo dữ liệu form thanh toán SePay.
    amount: số tiền VND (đơn vị nhỏ nhất, ví dụ 100000 = 100k VND)
    """
    if not settings.SEPAY_MERCHANT_ID or not settings.SEPAY_SECRET_KEY:
        raise ValueError("Chưa cấu hình SEPAY_MERCHANT_ID, SEPAY_SECRET_KEY")

    fields = {
        "merchant": settings.SEPAY_MERCHANT_ID,
        "currency": "VND",
        "order_amount": str(amount),
        "operation": "PURCHASE",
        "order_description": order_description[:255],
        "order_invoice_number": order_invoice_number,
        "success_url": success_url,
        "error_url": error_url,
        "cancel_url": cancel_url,
    }
    if customer_id:
        fields["customer_id"] = customer_id
    if payment_method:
        fields["payment_method"] = payment_method

    signature = _make_sepay_signature(fields, settings.SEPAY_SECRET_KEY)
    fields["signature"] = signature
    return fields


