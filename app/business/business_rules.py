"""
MVP business rules — single source of truth for defaults.

Review
------
- Chỉ DELIVERED/COMPLETED với sách trong đơn, trong REVIEW_WINDOW_DAYS kể từ lần giao mới nhất.
- Một user–một sách: một review active (soft-delete cho phép tạo lại sau khi xóa — theo repo hiện tại).
- Thưởng điểm: chỉ lần tạo review đầu tiên; idempotent theo (reason, ref_type=review, ref_id).

Book views
----------
- Debounce BOOK_VIEW_DEBOUNCE_MINUTES / user / book để tránh spam view count.

Checkout
--------
- Tối đa một mã voucher (promotion_code) mỗi đơn.
- Thứ tự: subtotal sách → giảm voucher % → giảm từ điểm (VND) → phí ship → total.
- Điểm đổi: LOYALTY_POINT_VALUE_VND (mỗi điểm = bao nhiêu VND giảm), trần LOYALTY_MAX_ORDER_POINTS_DISCOUNT_PERCENT % trên tiền sau voucher.

Notifications (WebSocket)
-------------------------
- Payload realtime kèm schema_version + meta (dict) để app không phụ thuộc parse message text.
"""

from app.core.config import get_settings

NOTIFICATION_WS_SCHEMA_VERSION = 1


def get_review_window_days() -> int:
    return max(1, int(get_settings().REVIEW_WINDOW_DAYS))


def get_book_view_debounce_minutes() -> int:
    return max(1, int(get_settings().BOOK_VIEW_DEBOUNCE_MINUTES))
