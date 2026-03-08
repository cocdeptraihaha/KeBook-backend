"""SupportRequest endpoints - yêu cầu hỗ trợ."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user, get_current_superuser
from app.core.database import get_db
from app.models.user import User
from app.schemas.support_request import SupportRequest, SupportRequestCreate, SupportRequestUpdate
from app.repositories.support_request_repository import support_request_repository

router = APIRouter()


@router.post("/", response_model=SupportRequest, status_code=status.HTTP_201_CREATED)
async def create_support_request(
    req_in: SupportRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """User submit support request."""
    from app.models.support_request import SupportRequest as SRModel
    from datetime import datetime
    req = SRModel(
        email=req_in.email or current_user.email,
        issue=req_in.issue,
        description=req_in.description,
        type=req_in.type,
        created_at=datetime.utcnow(),
        status="PENDING",
    )
    db.add(req)
    await db.flush()
    await db.refresh(req)
    return req


@router.get("/", response_model=list[SupportRequest])
async def list_support_requests(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """List support requests (admin)."""
    return await support_request_repository.get_multi(db, skip, limit)


@router.patch("/{req_id}", response_model=SupportRequest)
async def update_support_request(
    req_id: int,
    req_in: SupportRequestUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Admin phản hồi yêu cầu hỗ trợ."""
    from datetime import datetime
    req = await support_request_repository.get(db, req_id)
    if not req:
        raise HTTPException(status_code=404, detail="Not found")
    if req_in.staff_response is not None:
        req.staff_response = req_in.staff_response
        req.staff_id = current_user.id
        req.staff_name = current_user.full_name or current_user.username
    if req_in.status is not None:
        req.status = req_in.status
        if req_in.status == "RESOLVED":
            req.resolved_at = datetime.utcnow()
    await db.flush()
    await db.refresh(req)
    return req
