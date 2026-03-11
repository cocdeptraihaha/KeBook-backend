"""Book schemas."""
from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Optional, List, Tuple

from pydantic import BaseModel, Field, computed_field


class BookDiscountOut(BaseModel):
    discount_amount: Optional[float] = None
    discount_percent: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    model_config = {"from_attributes": True}


def _pick_active_discount(
    discounts: List[BookDiscountOut] | None, original_price: float | None
) -> Tuple[Optional[BookDiscountOut], float]:
    if not discounts or not original_price or original_price <= 0:
        return None, 0.0

    now = datetime.now(timezone.utc)
    best: Optional[BookDiscountOut] = None
    best_amount = 0.0

    for d in discounts:
        if d.start_date and d.start_date > now:
            continue
        if d.end_date and d.end_date < now:
            continue

        amount = 0.0
        if d.discount_percent is not None:
            amount = original_price * (d.discount_percent / 100.0)
        elif d.discount_amount is not None:
            amount = d.discount_amount
        if amount > best_amount:
            best_amount = amount
            best = d

    if best_amount <= 0:
        return None, 0.0
    return best, best_amount


class BookDetailBase(BaseModel):
    description: Optional[str] = None
    height: Optional[float] = None
    image_url: Optional[str] = None
    length: Optional[float] = None
    pages: Optional[int] = None
    publisher: Optional[str] = None
    supplier: Optional[str] = None
    weight: Optional[float] = None
    width: Optional[float] = None


class BookDetailCreate(BookDetailBase):
    pass


class BookDetailUpdate(BaseModel):
    description: Optional[str] = None
    height: Optional[float] = None
    image_url: Optional[str] = None
    length: Optional[float] = None
    pages: Optional[int] = None
    publisher: Optional[str] = None
    supplier: Optional[str] = None
    weight: Optional[float] = None
    width: Optional[float] = None


class BookDetail(BookDetailBase):
    id: int

    model_config = {"from_attributes": True}


class BookBase(BaseModel):
    author: Optional[str] = None
    code: Optional[str] = None
    edition: Optional[int] = None
    publication_date: Optional[date] = None
    selling_price: Optional[float] = None
    stock_quantity: Optional[int] = None
    title: Optional[str] = None
    book_detail_id: Optional[int] = None


class BookCreate(BookBase):
    pass


class BookCreateWithDetail(BookBase):
    """Create book with optional nested book_detail. If book_detail provided, creates both in one call."""
    book_detail: Optional[BookDetailCreate] = None


class BookUpdate(BaseModel):
    author: Optional[str] = None
    code: Optional[str] = None
    edition: Optional[int] = None
    publication_date: Optional[date] = None
    selling_price: Optional[float] = None
    stock_quantity: Optional[int] = None
    title: Optional[str] = None
    book_detail_id: Optional[int] = None


class Book(BookBase):
    id: int
    deleted_at: Optional[datetime] = None
    # Loaded via ORM relationship; excluded from API output but used for computed fields
    discounts: List[BookDiscountOut] = Field(default_factory=list, exclude=True)

    model_config = {"from_attributes": True}

    @computed_field  # type: ignore[misc]
    @property
    def original_price(self) -> Optional[float]:
        return self.selling_price

    @computed_field  # type: ignore[misc]
    @property
    def discount_amount(self) -> float:
        _, amt = _pick_active_discount(self.discounts, self.selling_price)
        return round(max(0.0, amt), 2)

    @computed_field  # type: ignore[misc]
    @property
    def discount_percent(self) -> Optional[float]:
        d, _ = _pick_active_discount(self.discounts, self.selling_price)
        if not d:
            return None
        return d.discount_percent

    @computed_field  # type: ignore[misc]
    @property
    def has_discount(self) -> bool:
        return self.discount_amount > 0

    @computed_field  # type: ignore[misc]
    @property
    def final_price(self) -> Optional[float]:
        if self.selling_price is None:
            return None
        return round(max(0.0, (self.selling_price or 0.0) - self.discount_amount), 2)


class BookWithDetail(Book):
    book_detail: Optional[BookDetail] = None
