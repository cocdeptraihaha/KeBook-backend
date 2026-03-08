"""ReturnRequest endpoints - yêu cầu trả hàng."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user, get_current_superuser
from app.core.database import get_db
from app.models.user import User
from app.schemas.return_request import ReturnRequest, ReturnRequestCreate, ReturnRequestProcess
from app.services.return_request_service import return_request_service

router = APIRouter()


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
