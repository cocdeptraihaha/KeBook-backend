"""ReturnRequest endpoints - yêu cầu trả hàng."""
from datetime import date, datetime, time
from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user, get_current_superuser
from app.core.database import get_db
from app.models.user import User
from app.schemas.return_request import (
    ReturnRequest,
    ReturnRequestAdminRow,
    ReturnRequestCreate,
    ReturnRequestProcess,
)
from app.services.return_request_service import return_request_service

router = APIRouter()


def _range_q(from_d: Optional[date], to_d: Optional[date]) -> tuple[Optional[datetime], Optional[datetime]]:
    from_dt = datetime.combine(from_d, time.min) if from_d else None
    to_dt = datetime.combine(to_d, time.max) if to_d else None
    return from_dt, to_dt


@router.get("/admin/all", response_model=list[ReturnRequestAdminRow])
async def admin_list_return_requests(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: Optional[Literal["PENDING", "APPROVED", "REJECTED"]] = Query(None),
    from_d: Optional[date] = Query(None, alias="from"),
    to_d: Optional[date] = Query(None, alias="to"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    """Admin: danh sách yêu cầu trả hàng (lọc theo trạng thái / ngày)."""
    from_dt, to_dt = _range_q(from_d, to_d)
    return await return_request_service.list_admin(
        db,
        skip=skip,
        limit=limit,
        status=status,
        from_dt=from_dt,
        to_dt=to_dt,
    )


@router.get("/", response_model=list[ReturnRequest])
async def get_my_return_requests(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get return requests of user."""
    return await return_request_service.get_by_user(
        db, current_user.id, skip, limit
    )


@router.post("/", response_model=ReturnRequest, status_code=status.HTTP_201_CREATED)
async def create_return_request(
    req_in: ReturnRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create return request."""
    try:
        return await return_request_service.create(db, req_in, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{req_id}/process", response_model=ReturnRequest)
async def process_return_request(
    req_id: int,
    body: ReturnRequestProcess,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Admin approve/reject return request."""
    req = await return_request_service.process(
        db, req_id, body.status, current_user.id
    )
    if not req:
        raise HTTPException(status_code=404, detail="Not found or already processed")
    return req
