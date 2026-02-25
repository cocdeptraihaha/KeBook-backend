"""SupportRequest model - yêu cầu hỗ trợ."""
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.core.database import Base


class SupportRequest(Base):
    """Bảng support_request."""

    __tablename__ = "support_request"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, nullable=True)
    description = Column(Text, nullable=True)
    email = Column(String(255), nullable=True)
    issue = Column(String(255), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    staff_id = Column(Integer, nullable=True)
    staff_name = Column(String(255), nullable=True)
    staff_response = Column(Text, nullable=True)
    status = Column(String(255), nullable=True)
    type = Column(String(255), nullable=True)
