"""SQLAlchemy models - kebookdb schema."""
from app.models.user import User
from app.models.otp import OTP, OTPType
from app.models.book_detail import BookDetail
from app.models.book import Book
from app.models.book_discount import BookDiscount
from app.models.book_book_discount import BookBookDiscount
from app.models.book_category import BookCategory
from app.models.category import Category
from app.models.payment import Payment, PaymentMethod
from app.models.service import Service
from app.models.promotion import Promotion
from app.models.cart import Cart
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.order_promotion import OrderPromotion
from app.models.order_status_history import OrderStatusHistory, OrderHistoryStatus
from app.models.return_request import ReturnRequest, ReturnRequestStatus
from app.models.review import Review
from app.models.notification import Notification
from app.models.user_notification import UserNotification
from app.models.support_request import SupportRequest
from app.models.user_promotion import UserPromotion
from app.models.point_transaction import PointTransaction
from app.models.favorite import Favorite
from app.models.book_view import BookView
from app.models.point_reward import PointReward

__all__ = [
    "User",
    "OTP",
    "OTPType",
    "BookDetail",
    "Book",
    "BookDiscount",
    "BookBookDiscount",
    "BookCategory",
    "Category",
    "Payment",
    "PaymentMethod",
    "Service",
    "Promotion",
    "Cart",
    "Order",
    "OrderStatus",
    "OrderItem",
    "OrderPromotion",
    "OrderStatusHistory",
    "OrderHistoryStatus",
    "ReturnRequest",
    "ReturnRequestStatus",
    "Review",
    "Notification",
    "UserNotification",
    "SupportRequest",
    "UserPromotion",
    "PointTransaction",
    "Favorite",
    "BookView",
    "PointReward",
]
