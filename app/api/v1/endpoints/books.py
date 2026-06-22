"""Book endpoints - sách."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import apaginate

from app.api.dependencies import get_current_active_user, get_current_superuser
from app.core.database import get_db
from app.models.user import User
from app.models.book_image import BookImage
from app.schemas.book import (
    Book as BookSchema,
    BookCategoriesPut,
    BookCreate,
    BookCreateWithDetail,
    BookImage as BookImageSchema,
    BookImageCreate,
    BookImageUpdate,
    BookUpdate,
    BookWithDetailOut,
)
from app.repositories.book_repository import book_repository, book_image_repository
from app.repositories.book_view_repository import book_view_repository
from app.services.book_service import book_service

router = APIRouter()


@router.get("/admin/all", response_model=Page[BookSchema])
async def admin_list_books(
    q: str | None = Query(None),
    category_id: int | None = Query(None),
    include_deleted: bool = Query(False),
    status: str | None = Query(None, description="active | deleted"),
    sort: str = Query("id", description="id | stock | selling_price | created_at"),
    order: str = Query("desc", description="asc | desc"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    stmt = book_service.build_admin_list_query(
        include_deleted=include_deleted,
        status=status,
        q=q,
        category_id=category_id,
        sort=sort,
        order=order,
    )
    return await apaginate(db, stmt)


@router.get("/admin/low-stock", response_model=list[BookSchema])
async def admin_low_stock_books(
    threshold: int = Query(5, ge=0, le=10000),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    rows = await book_service.list_low_stock(db, threshold=threshold, limit=limit)
    for b in rows:
        _ = list(b.discounts or [])
        _ = b.book_detail
        _ = list(b.images or [])
    return rows


@router.get("/", response_model=Page[BookSchema])
async def list_books(
    q: str | None = Query(None, description="Search by title, author"),
    category_id: int | None = Query(None, description="Filter books by category_id"),
    min_price: float | None = Query(None, description="Minimum price filter"),
    max_price: float | None = Query(None, description="Maximum price filter"),
    min_rating: float | None = Query(None, description="Minimum rating filter"),
    publisher: str | None = Query(None, description="Publisher name filter"),
    db: AsyncSession = Depends(get_db),
):
    """List books with pagination and advanced filtering."""
    stmt = book_service.build_list_query(
        q=q,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        publisher=publisher,
    )
    return await apaginate(db, stmt)


@router.get("/top-selling", response_model=list[BookSchema])
async def top_selling_books(
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Top N best-selling books by quantity."""
    return await book_service.get_top_selling(db, limit)


@router.get("/top-discounted", response_model=list[BookSchema])
async def top_discounted_books(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Top N books by biggest active discount amount."""
    return await book_service.get_top_discounted(db, limit)


@router.get("/{book_id}/similar", response_model=list[BookSchema])
async def similar_books(
    book_id: int,
    limit: int = Query(10, ge=1, le=30),
    db: AsyncSession = Depends(get_db),
):
    """Sách cùng thể loại (gợi ý tương tự)."""
    book = await book_service.repository.get(db, book_id)
    if not book or book.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Book not found")
    return await book_repository.get_similar_books(db, book_id, limit=limit)


@router.post("/{book_id}/view", status_code=status.HTTP_204_NO_CONTENT)
async def record_book_view(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Ghi nhận user đã xem sách (để đã xem + đếm lượt xem)."""
    book = await book_service.repository.get(db, book_id)
    if not book or book.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Book not found")
    from app.business.business_rules import get_book_view_debounce_minutes

    await book_view_repository.record_if_debounced(
        db,
        current_user.id,
        book_id,
        debounce_minutes=get_book_view_debounce_minutes(),
    )
    return None


@router.get("/{book_id}", response_model=BookWithDetailOut)
async def get_book(
    book_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Book detail + thống kê (public)."""
    book = await book_service.repository.get_with_detail(db, book_id)
    if not book or book.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Book not found")
    # Materialize quan hệ trong phiên async (tránh lazy-load khi serialize response)
    _ = list(book.discounts or [])
    _ = book.book_detail
    _ = list(book.images or [])
    bc, rc, vc = await book_repository.get_book_stats(db, book_id)
    out = BookWithDetailOut.model_validate(book, from_attributes=True)
    return out.model_copy(
        update={"buyer_count": bc, "review_count": rc, "view_count": vc}
    )


@router.post("/", response_model=BookSchema, status_code=status.HTTP_201_CREATED)
async def create_book(
    book_in: BookCreate | BookCreateWithDetail,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Create new book (admin only). Can include nested book_detail to create both in one call."""
    detail_in = getattr(book_in, "book_detail", None)
    data = {k: v for k, v in book_in.model_dump().items() if k != "book_detail"}
    book_data = BookCreate(**data)
    book = await book_service.create_book(db, book_data, detail_in=detail_in)
    full = await book_service.repository.get_with_detail(db, book.id)
    if full:
        _ = list(full.discounts or [])
        _ = full.book_detail
        _ = list(full.images or [])
        return full
    _ = list(book.discounts or [])
    _ = list(book.images or [])
    return book


@router.patch("/{book_id}", response_model=BookSchema)
async def update_book(
    book_id: int,
    book_in: BookUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Update book (admin only)."""
    book = await book_service.repository.get(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    book = await book_service.repository.update(db, book, book_in)
    full = await book_service.repository.get_with_detail(db, book.id)
    if full:
        _ = list(full.discounts or [])
        _ = full.book_detail
        _ = list(full.images or [])
        return full
    _ = list(book.discounts or [])
    _ = list(book.images or [])
    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def soft_delete_book(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    book = await book_service.soft_delete_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return None


@router.post("/{book_id}/restore", response_model=BookSchema)
async def restore_book(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    book = await book_service.restore_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    full = await book_service.repository.get_with_detail(db, book.id)
    if full:
        _ = list(full.discounts or [])
        _ = full.book_detail
        _ = list(full.images or [])
        return full
    _ = list(book.discounts or [])
    _ = list(book.images or [])
    return book


@router.put("/{book_id}/categories", response_model=BookSchema)
async def put_book_categories(
    book_id: int,
    body: BookCategoriesPut,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    try:
        full = await book_service.replace_book_categories(db, book_id, body.category_ids)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    _ = list(full.discounts or [])
    _ = full.book_detail
    _ = list(full.images or [])
    return full


@router.get("/{book_id}/images", response_model=list[BookImageSchema])
async def list_book_images(
    book_id: int,
    db: AsyncSession = Depends(get_db),
):
    book = await book_repository.get(db, book_id)
    if not book or book.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Book not found")
    return await book_image_repository.list_by_book(db, book_id)


@router.post("/{book_id}/images", response_model=BookImageSchema, status_code=status.HTTP_201_CREATED)
async def create_book_image(
    book_id: int,
    payload: BookImageCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    book = await book_repository.get(db, book_id)
    if not book or book.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Book not found")

    if payload.is_primary:
        await book_image_repository.clear_primary_for_book(db, book_id)

    created = BookImage(
        book_id=book_id,
        image_url=payload.image_url,
        sort_order=payload.sort_order,
        is_primary=payload.is_primary,
        alt_text=payload.alt_text,
    )
    db.add(created)
    await db.flush()

    await book_image_repository.ensure_single_primary(db, book_id)
    await book_image_repository.sync_legacy_image_url(db, book_id)
    await db.refresh(created)
    return created


@router.patch("/{book_id}/images/{image_id}", response_model=BookImageSchema)
async def update_book_image(
    book_id: int,
    image_id: int,
    payload: BookImageUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    image = await book_image_repository.get(db, image_id)
    if not image or image.book_id != book_id:
        raise HTTPException(status_code=404, detail="Book image not found")

    if payload.is_primary is True:
        await book_image_repository.clear_primary_for_book(db, book_id)

    updated = await book_image_repository.update(db, image, payload)
    await book_image_repository.ensure_single_primary(db, book_id)
    await book_image_repository.sync_legacy_image_url(db, book_id)
    await db.refresh(updated)
    return updated


@router.delete("/{book_id}/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book_image(
    book_id: int,
    image_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    image = await book_image_repository.get(db, image_id)
    if not image or image.book_id != book_id:
        raise HTTPException(status_code=404, detail="Book image not found")

    await db.delete(image)
    await db.flush()
    await book_image_repository.ensure_single_primary(db, book_id)
    await book_image_repository.sync_legacy_image_url(db, book_id)
    return None
