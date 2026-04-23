"""Book repository."""
from typing import Optional, List
from sqlalchemy import select, func, exists
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.book import Book
from app.models.book_detail import BookDetail
from app.models.book_category import BookCategory
from app.models.book_discount import BookDiscount
from app.models.book_book_discount import BookBookDiscount
from app.models.book_view import BookView
from app.models.order_item import OrderItem
from app.models.order import Order, OrderStatus
from app.models.review import Review
from app.models.category import Category
from app.schemas.book import BookCreate, BookUpdate, BookDetailCreate, BookDetailUpdate
from app.repositories.base_repository import BaseRepository


class BookRepository(BaseRepository[Book, BookCreate, BookUpdate]):
    """Repository cho Book."""

    async def get_with_detail(self, db: AsyncSession, id: int) -> Optional[Book]:
        """Lấy book kèm book_detail."""
        result = await db.execute(
            select(Book)
            .where(Book.id == id)
            .options(selectinload(Book.book_detail), selectinload(Book.discounts))
        )
        return result.scalars().first()

    async def get_multi_active(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Book]:
        """Lấy danh sách book chưa xóa."""
        result = await db.execute(
            select(Book)
            .where(Book.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def search(
        self,
        db: AsyncSession,
        q: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Book]:
        """Tìm sách theo title, author."""
        stmt = select(Book).where(Book.deleted_at.is_(None))
        if q:
            stmt = stmt.where(
                (Book.title.like(f"%{q}%")) | (Book.author.like(f"%{q}%"))
            )
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    def build_list_query(
        self,
        q: Optional[str] = None,
        category_id: Optional[int] = None,
    ):
        """Build a select statement for paginated book listing."""
        from sqlalchemy import or_

        stmt = (
            select(Book)
            .join(BookDetail, Book.book_detail_id == BookDetail.id, isouter=True)
            .options(selectinload(Book.discounts), selectinload(Book.book_detail))
        )

        if category_id is not None:
            cat_tree = (
                select(Category.id)
                .where(Category.id == category_id)
                .cte(name="cat_tree", recursive=True)
            )
            cat_tree = cat_tree.union_all(
                select(Category.id).join(cat_tree, Category.parent_id == cat_tree.c.id)
            )
            stmt = stmt.where(
                exists(
                    select(1)
                    .select_from(BookCategory)
                    .where(BookCategory.book_id == Book.id)
                    .where(BookCategory.category_id.in_(select(cat_tree.c.id)))
                )
            )
        else:
            stmt = stmt.join(BookCategory, BookCategory.book_id == Book.id, isouter=True)

        stmt = stmt.where(Book.deleted_at.is_(None)).order_by(Book.id)
        if q:
            pattern = f"%{q.lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(Book.title).like(pattern),
                    func.lower(Book.author).like(pattern),
                    func.lower(BookDetail.description).like(pattern),
                    func.lower(BookDetail.publisher).like(pattern),
                    func.lower(BookDetail.supplier).like(pattern),
                )
            )
        return stmt

    async def get_top_selling(self, db: AsyncSession, limit: int = 10) -> List[Book]:
        """Top N best-selling books by order quantity."""
        qty_subq = (
            select(
                OrderItem.book_id.label("book_id"),
                func.sum(OrderItem.quantity).label("total_qty"),
            )
            .where(OrderItem.deleted_at.is_(None), OrderItem.book_id.is_not(None))
            .group_by(OrderItem.book_id)
            .subquery()
        )
        stmt = (
            select(Book)
            .join(qty_subq, Book.id == qty_subq.c.book_id)
            .options(selectinload(Book.book_detail), selectinload(Book.discounts))
            .where(Book.deleted_at.is_(None))
            .order_by(qty_subq.c.total_qty.desc())
            .limit(limit)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_top_discounted(self, db: AsyncSession, limit: int = 20) -> List[Book]:
        """Top N books by biggest active discount amount."""
        now = func.now()
        percent_amount = (
            func.coalesce(Book.selling_price, 0)
            * func.coalesce(BookDiscount.discount_percent, 0)
            / 100.0
        )
        amount_expr = func.greatest(
            func.coalesce(BookDiscount.discount_amount, 0),
            func.coalesce(percent_amount, 0),
        )
        disc_subq = (
            select(
                BookBookDiscount.book_id.label("book_id"),
                func.max(amount_expr).label("best_discount"),
            )
            .join(BookDiscount, BookDiscount.id == BookBookDiscount.discount_id)
            .join(Book, Book.id == BookBookDiscount.book_id)
            .where(
                Book.deleted_at.is_(None),
                func.coalesce(BookDiscount.start_date, now) <= now,
                func.coalesce(BookDiscount.end_date, now) >= now,
            )
            .group_by(BookBookDiscount.book_id)
            .subquery()
        )
        stmt = (
            select(Book)
            .join(disc_subq, Book.id == disc_subq.c.book_id)
            .options(selectinload(Book.book_detail), selectinload(Book.discounts))
            .where(Book.deleted_at.is_(None))
            .order_by(disc_subq.c.best_discount.desc())
            .limit(limit)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_book_stats(
        self, db: AsyncSession, book_id: int
    ) -> tuple[int, int, int]:
        """(buyer_count, review_count, view_count)."""
        r_rev = await db.execute(
            select(func.count(Review.id)).where(
                Review.book_id == book_id,
                Review.deleted_at.is_(None),
            )
        )
        review_count = int(r_rev.scalar() or 0)
        r_buy = await db.execute(
            select(func.count(func.distinct(Order.user_id)))
            .select_from(OrderItem)
            .join(Order, Order.id == OrderItem.order_id)
            .where(
                OrderItem.book_id == book_id,
                OrderItem.deleted_at.is_(None),
                Order.deleted_at.is_(None),
                Order.status.in_((OrderStatus.DELIVERED, OrderStatus.COMPLETED)),
            )
        )
        buyer_count = int(r_buy.scalar() or 0)
        r_view = await db.execute(
            select(func.count(BookView.id)).where(BookView.book_id == book_id)
        )
        view_count = int(r_view.scalar() or 0)
        return buyer_count, review_count, view_count

    async def get_similar_books(
        self, db: AsyncSession, book_id: int, limit: int = 10
    ) -> List[Book]:
        r_cat = await db.execute(
            select(BookCategory.category_id).where(BookCategory.book_id == book_id)
        )
        cat_ids = [row[0] for row in r_cat.all()]
        if not cat_ids:
            return []
        r_ids = await db.execute(
            select(Book.id)
            .join(BookCategory, BookCategory.book_id == Book.id)
            .where(
                BookCategory.category_id.in_(cat_ids),
                Book.id != book_id,
                Book.deleted_at.is_(None),
            )
            .distinct()
        )
        ids = [row[0] for row in r_ids.all()]
        if not ids:
            return []
        r_cnt = await db.execute(
            select(BookView.book_id, func.count(BookView.id))
            .where(BookView.book_id.in_(ids))
            .group_by(BookView.book_id)
        )
        counts = {bid: int(c) for bid, c in r_cnt.all()}
        ids.sort(key=lambda i: (-counts.get(i, 0), i))
        ids = ids[:limit]
        r_books = await db.execute(
            select(Book)
            .where(Book.id.in_(ids))
            .options(selectinload(Book.book_detail), selectinload(Book.discounts))
        )
        by_id = {b.id: b for b in r_books.scalars().all()}
        return [by_id[i] for i in ids if i in by_id]

    def build_admin_list_query(
        self,
        *,
        include_deleted: bool = False,
        status: Optional[str] = None,
        q: Optional[str] = None,
        category_id: Optional[int] = None,
        sort: str = "id",
        order: str = "desc",
    ):
        """Select sách cho admin (lọc xóa mềm, sort)."""
        from sqlalchemy import or_

        stmt = (
            select(Book)
            .join(BookDetail, Book.book_detail_id == BookDetail.id, isouter=True)
            .options(selectinload(Book.discounts), selectinload(Book.book_detail))
        )
        if category_id is not None:
            stmt = stmt.where(
                exists(
                    select(1)
                    .select_from(BookCategory)
                    .where(
                        BookCategory.book_id == Book.id,
                        BookCategory.category_id == category_id,
                    )
                )
            )

        st = (status or "active").lower()
        if st == "deleted":
            stmt = stmt.where(Book.deleted_at.is_not(None))
        elif include_deleted:
            pass
        else:
            stmt = stmt.where(Book.deleted_at.is_(None))

        if q:
            pattern = f"%{q.lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(Book.title).like(pattern),
                    func.lower(Book.author).like(pattern),
                    func.lower(BookDetail.description).like(pattern),
                    func.lower(BookDetail.publisher).like(pattern),
                    func.lower(BookDetail.supplier).like(pattern),
                )
            )

        sort_key = (sort or "id").lower()
        ord_key = (order or "desc").lower()
        col_map = {
            "id": Book.id,
            "stock": Book.stock_quantity,
            "selling_price": Book.selling_price,
            "created_at": Book.id,
        }
        col = col_map.get(sort_key, Book.id)
        if ord_key == "asc":
            stmt = stmt.order_by(col.asc())
        else:
            stmt = stmt.order_by(col.desc())
        return stmt

    async def list_low_stock(
        self,
        db: AsyncSession,
        *,
        threshold: int = 5,
        limit: int = 50,
    ) -> List[Book]:
        stmt = (
            select(Book)
            .where(
                Book.deleted_at.is_(None),
                Book.stock_quantity.is_not(None),
                Book.stock_quantity <= threshold,
            )
            .options(selectinload(Book.book_detail), selectinload(Book.discounts))
            .order_by(Book.stock_quantity.asc(), Book.id)
            .limit(limit)
        )
        r = await db.execute(stmt)
        return list(r.scalars().all())


class BookDetailRepository(BaseRepository[BookDetail, BookDetailCreate, BookDetailUpdate]):
    """Repository cho BookDetail."""

    pass


book_repository = BookRepository(Book)
book_detail_repository = BookDetailRepository(BookDetail)
