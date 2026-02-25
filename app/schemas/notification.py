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


class Notification(NotificationBase):
    id: int
    send_date: Optional[datetime] = None
    is_deleted: bool = False

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
