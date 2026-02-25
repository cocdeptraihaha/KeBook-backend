"""Cart endpoints - giỏ hàng."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.cart import Cart, CartCreate, CartUpdate
from app.services.cart_service import cart_service

router = APIRouter()


@router.get("/", response_model=list[Cart])
async def get_my_cart(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Lấy giỏ hàng của user đăng nhập."""
    return await cart_service.get_user_cart(db, current_user.id, skip, limit)


@router.post("/", response_model=Cart, status_code=status.HTTP_201_CREATED)
async def add_to_cart(
    cart_in: CartCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Thêm sách vào giỏ hàng."""
    return await cart_service.add_to_cart(db, current_user.id, cart_in)


@router.patch("/{cart_id}", response_model=Cart)
async def update_cart_item(
    cart_id: int,
    cart_in: CartUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Cập nhật số lượng trong giỏ."""
    if cart_in.quantity is None:
        raise HTTPException(status_code=400, detail="Cần có quantity")
    cart = await cart_service.update_quantity(
        db, cart_id, current_user.id, cart_in.quantity
    )
    if not cart:
        raise HTTPException(status_code=404, detail="Không tìm thấy item")
    return cart


@router.delete("/{cart_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_cart(
    cart_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Xóa item khỏi giỏ hàng."""
    ok = await cart_service.remove_from_cart(db, cart_id, current_user.id)
    if not ok:
        raise HTTPException(status_code=404, detail="Không tìm thấy item")
