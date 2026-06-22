"""Notification schemas."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class NotificationType(str, Enum):
    GENERIC = "GENERIC"
    WELCOME = "WELCOME"
    POINTS_EARNED = "POINTS_EARNED"
    CAMPAIGN = "CAMPAIGN"

    ORDER_NEW = "ORDER_NEW"
    ORDER_SHIPMENT = "ORDER_SHIPMENT"
    ORDER_SHIPPED = "ORDER_SHIPPED"

    ORDER_STATUS_PENDING = "ORDER_STATUS_PENDING"
    ORDER_STATUS_CONFIRMED = "ORDER_STATUS_CONFIRMED"
    ORDER_STATUS_INPROGRESS = "ORDER_STATUS_INPROGRESS"
    ORDER_STATUS_SHIPPED = "ORDER_STATUS_SHIPPED"
    ORDER_STATUS_DELIVERED = "ORDER_STATUS_DELIVERED"
    ORDER_STATUS_COMPLETED = "ORDER_STATUS_COMPLETED"
    ORDER_STATUS_CANCELLED = "ORDER_STATUS_CANCELLED"
    ORDER_STATUS_CANCEL_REQUESTED = "ORDER_STATUS_CANCEL_REQUESTED"
    ORDER_STATUS_RETURNED = "ORDER_STATUS_RETURNED"

    REVIEW_NEW = "REVIEW_NEW"
    SUPPORT_NEW = "SUPPORT_NEW"


class NotificationBase(BaseModel):
    # message stores machine-readable JSON payload (ids/metadata).
    message: Optional[str] = None
    title: Optional[str] = None
    type: Optional[NotificationType] = None


class NotificationCreate(NotificationBase):
    pass


class NotificationSendRequest(NotificationBase):
    user_ids: list[int] = []


class UserFilter(BaseModel):
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


class NotificationBroadcastRequest(NotificationBase):
    """Broadcast via user_ids, or user_filter, or all users."""

    user_ids: Optional[list[int]] = None
    user_filter: Optional[UserFilter] = None


class Notification(NotificationBase):
    id: int
    send_date: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class NotificationOut(Notification):
    payload: Dict[str, Any] = Field(default_factory=dict)


class UserNotificationBase(BaseModel):
    notification_id: int
    user_id: int


class UserNotificationCreate(UserNotificationBase):
    pass


class UserNotification(UserNotificationBase):
    is_read: Optional[bool] = None
    read_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class UserNotificationOut(BaseModel):
    notification_id: int
    user_id: int
    is_read: Optional[bool] = None
    read_at: Optional[datetime] = None
    notification: NotificationOut

    model_config = {"from_attributes": True}
