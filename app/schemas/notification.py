"""Notification schemas."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class NotificationBase(BaseModel):
    message: Optional[str] = None
    title: Optional[str] = None
    type: Optional[str] = None


class NotificationCreate(NotificationBase):
    pass


class NotificationSendRequest(NotificationBase):
    user_ids: list[int] = []


class UserFilter(BaseModel):
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


class NotificationBroadcastRequest(NotificationBase):
    """Gửi hàng loạt: `user_ids` cụ thể, hoặc `user_filter`, hoặc bỏ cả hai = tất cả user."""

    user_ids: Optional[list[int]] = None
    user_filter: Optional[UserFilter] = None


class Notification(NotificationBase):
    id: int
    send_date: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class UserNotificationBase(BaseModel):
    notification_id: int
    user_id: int


class UserNotificationCreate(UserNotificationBase):
    pass


class UserNotification(UserNotificationBase):
    is_read: Optional[bool] = None
    read_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
