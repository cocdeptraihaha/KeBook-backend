import hashlib
import hmac
import urllib.parse
from datetime import datetime
from typing import Dict
from app.core.config import get_settings


class VNPayService:
    """VNPay Payment integration utility."""

    @staticmethod
    def generate_payment_url(
        order_id: int, amount: float, ip_address: str, order_info: str = ""
    ) -> str:
        settings = get_settings()
        vnp_tmn_code = settings.VNPAY_TMN_CODE
        vnp_hash_secret = settings.VNPAY_HASH_SECRET
        vnp_url = settings.VNPAY_URL
        vnp_return_url = settings.VNPAY_RETURN_URL

        create_date = datetime.now().strftime("%Y%m%d%H%M%S")
        vnp_params = {
            "vnp_Version": "2.1.0",
            "vnp_Command": "pay",
            "vnp_TmnCode": vnp_tmn_code,
            "vnp_Amount": str(int(amount * 100)),  # VNPAY expects amount in VND multiplied by 100
            "vnp_CreateDate": create_date,
            "vnp_CurrCode": "VND",
            "vnp_IpAddr": ip_address,
            "vnp_Locale": "vn",
            "vnp_OrderInfo": order_info or f"Thanh toan don hang #{order_id}",
            "vnp_OrderType": "other",
            "vnp_ReturnUrl": vnp_return_url,
            "vnp_TxnRef": f"{order_id}_{create_date}",
        }

        # Sort parameters alphabetically as required by VNPay
        sorted_params = sorted(vnp_params.items())
        query_string = urllib.parse.urlencode(sorted_params)

        # Calculate secure hash signature
        signature = hmac.new(
            vnp_hash_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha512
        ).hexdigest()

        return f"{vnp_url}?{query_string}&vnp_SecureHash={signature}"

    @staticmethod
    def verify_signature(params: Dict[str, str]) -> bool:
        """Verify hash signatures received back from VNPay callback/IPN redirects."""
        settings = get_settings()
        vnp_hash_secret = settings.VNPAY_HASH_SECRET

        vnp_secure_hash = params.get("vnp_SecureHash")
        if not vnp_secure_hash:
            return False

        # Filter out secure hash variables for sorting
        hash_params = {k: v for k, v in params.items() if k.startswith("vnp_") and k != "vnp_SecureHash" and k != "vnp_SecureHashType"}
        sorted_params = sorted(hash_params.items())
        query_string = urllib.parse.urlencode(sorted_params)

        calculated_signature = hmac.new(
            vnp_hash_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha512
        ).hexdigest()

        return calculated_signature == vnp_secure_hash


vnpay_service = VNPayService()
