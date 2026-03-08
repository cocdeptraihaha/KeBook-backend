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


class CheckoutRequest(BaseModel):
    """Checkout từ giỏ hàng."""
    note: Optional[str] = None
    phone_number: Optional[str] = None
    shipping_address: Optional[str] = None
    promotion_code: Optional[str] = None


class OrderUpdate(BaseModel):
    note: Optional[str] = None
    phone_number: Optional[str] = None
    shipping_address: Optional[str] = None
    status: Optional[str] = None


class OrderStatusUpdate(BaseModel):
    status: str  # PENDING, CONFIRMED, INPROGRESS, SHIPPED, DELIVERED, COMPLETED, CANCELLED, RETURNED


class Order(OrderBase):
    id: int
    order_date: Optional[datetime] = None
    status: Optional[str] = None
    total_price: Optional[float] = None
    user_id: int = 0
    deleted_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class OrderWithItems(Order):
    order_items: List[OrderItem] = []
