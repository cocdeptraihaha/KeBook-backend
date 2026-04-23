"""SupportRequest endpoints - yêu cầu hỗ trợ."""
from datetime import date, datetime, time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user, get_current_superuser
from app.core.database import get_db
from app.models.user import User
from app.schemas.support_request import (
    SupportRequest,
    SupportRequestCreate,
    SupportRequestStatusPatch,
    SupportRequestUpdate,
)
from app.services.support_request_service import support_request_service

router = APIRouter()


@router.post("/", response_model=SupportRequest, status_code=status.HTTP_201_CREATED)
async def create_support_request(
    req_in: SupportRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """User submit support request."""
    return await support_request_service.create(db, req_in, current_user.email)


@router.get("/", response_model=list[SupportRequest])
async def list_support_requests(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    from_d: Optional[date] = Query(None, alias="from"),
    to_d: Optional[date] = Query(None, alias="to"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """List support requests (admin)."""
    from_dt = datetime.combine(from_d, time.min) if from_d else None
    to_dt = datetime.combine(to_d, time.max) if to_d else None
    return await support_request_service.get_all(
        db, skip, limit, status=status, q=q, from_dt=from_dt, to_dt=to_dt
    )


@router.patch("/{req_id}/status", response_model=SupportRequest)
async def patch_support_request_status(
    req_id: int,
    body: SupportRequestStatusPatch,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    req_in = SupportRequestUpdate(status=body.status, staff_response=body.note)
    req = await support_request_service.respond(
        db,
        req_id,
        req_in,
        staff_id=current_user.id,
        staff_name=current_user.full_name or current_user.username,
    )
    if not req:
        raise HTTPException(status_code=404, detail="Not found")
    return req


@router.patch("/{req_id}", response_model=SupportRequest)
async def update_support_request(
    req_id: int,
    req_in: SupportRequestUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Admin phản hồi yêu cầu hỗ trợ."""
    req = await support_request_service.respond(
        db, req_id, req_in,
        staff_id=current_user.id,
        staff_name=current_user.full_name or current_user.username,
    )
    if not req:
        raise HTTPException(status_code=404, detail="Not found")
    return req
