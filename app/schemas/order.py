"""Order schemas."""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class OrderItemBase(BaseModel):
    book_id: Optional[int] = None
    quantity: int = 1
    price: float = 0


class OrderItemCreate(OrderItemBase):
    pass


class OrderItem(OrderItemBase):
    id: int
    book_title: Optional[str] = None
    image_url: Optional[str] = None
    order_id: Optional[int] = None
    deleted_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class OrderBase(BaseModel):
    note: Optional[str] = None
    phone_number: Optional[str] = None
    shipping_address: Optional[str] = None
    payment_id: int = 0
    service_id: int = 0


class OrderCreate(OrderBase):
    items: List[OrderItemCreate] = []
    user_id: int = 0
    promotion_code: Optional[str] = None


class CheckoutItemIn(BaseModel):
    book_id: int
    quantity: int = 1


class CheckoutRequest(BaseModel):
    """Checkout từ giỏ hàng hoặc danh sách items cụ thể."""
    address_id: Optional[int] = None
    full_name: Optional[str] = None
    note: Optional[str] = None
    phone_number: Optional[str] = None
    shipping_address: Optional[str] = None
    province: Optional[str] = None
    ward: Optional[str] = None
    promotion_code: Optional[str] = None
    payment_method: Optional[str] = "COD"  # COD, VNPAY, MOMO, SEPAY etc.
    """Số điểm tích lũy muốn đổi (VND giảm = điểm × LOYALTY_POINT_VALUE_VND), sau voucher, trong trần %."""
    loyalty_points_to_redeem: Optional[int] = None
    items: Optional[List[CheckoutItemIn]] = None


class OrderUpdate(BaseModel):
    note: Optional[str] = None
    phone_number: Optional[str] = None
    shipping_address: Optional[str] = None
    status: Optional[str] = None


class OrderStatusUpdate(BaseModel):
    status: str
    description: Optional[str] = None


class CancelOrderRequest(BaseModel):
    reason: Optional[str] = None


class CancelDecisionRequest(BaseModel):
    """Admin duyệt / từ chối yêu cầu hủy đơn (khi status == CANCEL_REQUESTED)."""

    approve: bool
    description: Optional[str] = None


class OrderStatusHistoryOut(BaseModel):
    id: int
    status: Optional[str] = None
    status_change_date: Optional[datetime] = None
    description: Optional[str] = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_model(cls, obj) -> "OrderStatusHistoryOut":
        return cls(
            id=obj.id,
            status=obj.e_order_history.value if obj.e_order_history else None,
            status_change_date=obj.status_change_date,
            description=getattr(obj, "description", None),
        )


class Order(OrderBase):
    id: int
    full_name: Optional[str] = None
    order_date: Optional[datetime] = None
    status: Optional[str] = None
    total_price: Optional[float] = None
    user_id: int = 0
    address_id: Optional[int] = None
    deleted_at: Optional[datetime] = None
    tracking_number: Optional[str] = None
    shipping_provider: Optional[str] = None
    payment_method: Optional[str] = None
    payment_status: Optional[str] = None

    model_config = {"from_attributes": True}


class OrderWithItems(Order):
    order_items: List[OrderItem] = []
    status_history: List[OrderStatusHistoryOut] = []


class OrderCheckoutOut(BaseModel):
    order: OrderWithItems
    item_amount: float
    discount_total: float
    shipping_fee: float
    total_amount: float
    loyalty_points_redeemed: int = 0
    points_discount_amount: float = 0.0
    payment_url: Optional[str] = None


class MoneyBucket(BaseModel):
    count: int
    total: float


class OrderMoneyStats(BaseModel):
    """Thống kê dòng tiền đơn hàng theo nhóm trạng thái (user)."""

    pending_confirm: MoneyBucket
    shipping: MoneyBucket
    delivered: MoneyBucket
    cancelled: MoneyBucket
    total_spent: float  # chỉ nhóm đã giao (DELIVERED + COMPLETED)


class OrderRevenueStats(OrderMoneyStats):
    """Cùng cấu trúc OrderMoneyStats; `total_spent` = doanh thu đã giao (admin toàn shop)."""

    pass


class RevenueTimeseriesRow(BaseModel):
    period: str
    order_count: int
    revenue: float


class OrderShipmentUpdate(BaseModel):
    tracking_number: Optional[str] = None
    shipping_provider: Optional[str] = None
