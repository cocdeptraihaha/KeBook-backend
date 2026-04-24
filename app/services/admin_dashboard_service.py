"""Tổng hợp số liệu dashboard admin."""
from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.book import Book
from app.models.book_category import BookCategory
from app.models.category import Category
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.user import User
from app.repositories.book_repository import book_repository
from app.services.order_service import order_service


class AdminDashboardService:
    async def summary(
        self,
        db: AsyncSession,
        *,
        from_dt: Optional[datetime] = None,
        to_dt: Optional[datetime] = None,
    ) -> dict:
        money = await order_service.get_money_stats(
            db, user_id=None, from_dt=from_dt, to_dt=to_dt
        )
        revenue = float(money.total_spent)

        o_stmt = select(func.count(Order.id)).where(Order.deleted_at.is_(None))
        if from_dt is not None:
            o_stmt = o_stmt.where(Order.order_date >= from_dt)
        if to_dt is not None:
            o_stmt = o_stmt.where(Order.order_date <= to_dt)
        order_count = int((await db.execute(o_stmt)).scalar() or 0)
        aov = (revenue / order_count) if order_count else 0.0

        u_stmt = select(func.count(User.id)).where(User.deleted_at.is_(None))
        if from_dt is not None:
            u_stmt = u_stmt.where(User.created_at >= from_dt)
        if to_dt is not None:
            u_stmt = u_stmt.where(User.created_at <= to_dt)
        new_user_count = int((await db.execute(u_stmt)).scalar() or 0)

        low_rows = await book_repository.list_low_stock(db, threshold=5, limit=500)
        low_stock_count = len(low_rows)

        pend_stmt = select(func.count(Order.id)).where(
            Order.deleted_at.is_(None),
            Order.status.in_([OrderStatus.PENDING, OrderStatus.CONFIRMED]),
        )
        if from_dt is not None:
            pend_stmt = pend_stmt.where(Order.order_date >= from_dt)
        if to_dt is not None:
            pend_stmt = pend_stmt.where(Order.order_date <= to_dt)
        pending_order_count = int((await db.execute(pend_stmt)).scalar() or 0)

        return {
            "revenue": revenue,
            "order_count": order_count,
            "aov": round(aov, 2),
            "new_user_count": new_user_count,
            "low_stock_count": low_stock_count,
            "pending_order_count": pending_order_count,
        }

    async def top_books(
        self,
        db: AsyncSession,
        *,
        from_dt: Optional[datetime] = None,
        to_dt: Optional[datetime] = None,
        limit: int = 10,
        metric: str = "revenue",
    ) -> List[dict]:
        qty_expr = func.coalesce(OrderItem.quantity, 0)
        line_rev = qty_expr * func.coalesce(OrderItem.price, 0.0)
        stmt = (
            select(
                OrderItem.book_id,
                func.sum(qty_expr).label("qty"),
                func.coalesce(func.sum(line_rev), 0.0).label("rev"),
            )
            .join(Order, Order.id == OrderItem.order_id)
            .where(
                OrderItem.deleted_at.is_(None),
                OrderItem.book_id.is_not(None),
                Order.deleted_at.is_(None),
                Order.status.in_([OrderStatus.DELIVERED, OrderStatus.COMPLETED]),
            )
            .group_by(OrderItem.book_id)
        )
        if from_dt is not None:
            stmt = stmt.where(Order.order_date >= from_dt)
        if to_dt is not None:
            stmt = stmt.where(Order.order_date <= to_dt)
        if metric == "quantity":
            stmt = stmt.order_by(func.sum(qty_expr).desc())
        else:
            stmt = stmt.order_by(func.coalesce(func.sum(line_rev), 0.0).desc())
        stmt = stmt.limit(limit)
        r = await db.execute(stmt)
        rows = r.all()
        if not rows:
            return []
        book_ids = [int(bid) for bid, _, _ in rows if bid is not None]
        titles: dict[int, str] = {}
        if book_ids:
            rb = await db.execute(select(Book.id, Book.title).where(Book.id.in_(book_ids)))
            titles = {i: (t or "") for i, t in rb.all()}
        out: List[dict] = []
        for bid, qty, rev in rows:
            if bid is None:
                continue
            bid = int(bid)
            out.append(
                {
                    "book_id": bid,
                    "title": titles.get(bid),
                    "quantity_sold": int(qty or 0),
                    "revenue": float(rev or 0),
                }
            )
        return out

    async def revenue_by_category(
        self,
        db: AsyncSession,
        *,
        from_dt: Optional[datetime] = None,
        to_dt: Optional[datetime] = None,
    ) -> List[dict]:
        qty_expr = func.coalesce(OrderItem.quantity, 0)
        line_rev = qty_expr * func.coalesce(OrderItem.price, 0.0)
        stmt = (
            select(
                BookCategory.category_id,
                func.coalesce(func.sum(line_rev), 0.0).label("rev"),
                func.count(func.distinct(Order.id)).label("oc"),
            )
            .select_from(OrderItem)
            .join(Order, Order.id == OrderItem.order_id)
            .join(BookCategory, BookCategory.book_id == OrderItem.book_id)
            .where(
                OrderItem.deleted_at.is_(None),
                OrderItem.book_id.is_not(None),
                Order.deleted_at.is_(None),
                Order.status.in_([OrderStatus.DELIVERED, OrderStatus.COMPLETED]),
            )
            .group_by(BookCategory.category_id)
        )
        if from_dt is not None:
            stmt = stmt.where(Order.order_date >= from_dt)
        if to_dt is not None:
            stmt = stmt.where(Order.order_date <= to_dt)
        r = await db.execute(stmt)
        cat_rows = r.all()
        if not cat_rows:
            return []
        cids = [int(c) for c, _, _ in cat_rows]
        names: dict[int, str] = {}
        if cids:
            rc = await db.execute(select(Category.id, Category.name).where(Category.id.in_(cids)))
            names = {i: (n or "") for i, n in rc.all()}
        return [
            {
                "category_id": int(cid),
                "category_name": names.get(int(cid)),
                "revenue": float(rev or 0),
                "order_count": int(oc or 0),
            }
            for cid, rev, oc in cat_rows
        ]

    async def user_timeseries(
        self,
        db: AsyncSession,
        *,
        from_dt: Optional[datetime] = None,
        to_dt: Optional[datetime] = None,
        group_by: str = "day",
    ) -> List[dict]:
        gb = (group_by or "day").lower()
        if gb == "day":
            end = to_dt or datetime.utcnow()
            end_day = datetime(end.year, end.month, end.day, 23, 59, 59, 999999)
            start_day = datetime(end.year, end.month, end.day) - timedelta(days=13)

            stmt = (
                select(func.date(User.created_at).label("period"), func.count(User.id))
                .where(
                    User.deleted_at.is_(None),
                    User.created_at >= start_day,
                    User.created_at <= end_day,
                )
                .group_by(func.date(User.created_at))
                .order_by(func.date(User.created_at))
            )
            r = await db.execute(stmt)
            per: dict[str, int] = {}
            for period, cnt in r.all():
                key = period.isoformat() if hasattr(period, "isoformat") else str(period)
                per[key] = int(cnt or 0)

            return [
                {
                    "period": (start_day + timedelta(days=i)).date().isoformat(),
                    "new_users": per.get((start_day + timedelta(days=i)).date().isoformat(), 0),
                }
                for i in range(14)
            ]

        if gb == "month":
            period_expr = func.date_format(User.created_at, "%Y-%m-01")
        elif gb == "week":
            period_expr = func.date_format(User.created_at, "%X-W%V")
        else:
            period_expr = func.date(User.created_at)

        stmt = (
            select(period_expr.label("period"), func.count(User.id))
            .where(User.deleted_at.is_(None))
            .group_by(period_expr)
            .order_by(period_expr)
        )
        if from_dt is not None:
            stmt = stmt.where(User.created_at >= from_dt)
        if to_dt is not None:
            stmt = stmt.where(User.created_at <= to_dt)
        r = await db.execute(stmt)
        out: List[dict] = []
        for period, cnt in r.all():
            p = period
            if hasattr(p, "isoformat"):
                p = p.isoformat()
            elif p is not None:
                p = str(p)
            else:
                p = ""
            out.append({"period": p, "new_users": int(cnt or 0)})
        return out


    async def get_top_customers(
        self,
        db: AsyncSession,
        *,
        from_dt: Optional[datetime] = None,
        to_dt: Optional[datetime] = None,
        limit: int = 10,
    ) -> List[dict]:
        stmt = (
            select(
                User.id,
                User.full_name,
                User.email,
                func.count(Order.id).label("order_count"),
                func.coalesce(func.sum(Order.total_price), 0.0).label("total_spent"),
            )
            .join(Order, Order.user_id == User.id)
            .where(
                User.deleted_at.is_(None),
                Order.deleted_at.is_(None),
                Order.status.in_([OrderStatus.DELIVERED, OrderStatus.COMPLETED]),
            )
            .group_by(User.id, User.full_name, User.email)
            .order_by(func.coalesce(func.sum(Order.total_price), 0.0).desc())
            .limit(limit)
        )
        if from_dt is not None:
            stmt = stmt.where(Order.order_date >= from_dt)
        if to_dt is not None:
            stmt = stmt.where(Order.order_date <= to_dt)
        r = await db.execute(stmt)
        out: List[dict] = []
        for uid, fn, em, oc, ts in r.all():
            out.append(
                {
                    "user_id": int(uid),
                    "full_name": fn,
                    "email": em,
                    "order_count": int(oc or 0),
                    "total_spent": float(ts or 0),
                }
            )
        return out

    async def order_status_breakdown(
        self,
        db: AsyncSession,
        *,
        from_dt: Optional[datetime] = None,
        to_dt: Optional[datetime] = None,
    ) -> List[dict]:
        stmt = (
            select(
                Order.status,
                func.count(Order.id),
                func.coalesce(func.sum(Order.total_price), 0.0),
            )
            .where(Order.deleted_at.is_(None))
            .group_by(Order.status)
        )
        if from_dt is not None:
            stmt = stmt.where(Order.order_date >= from_dt)
        if to_dt is not None:
            stmt = stmt.where(Order.order_date <= to_dt)
        r = await db.execute(stmt)
        per: dict[str, tuple[int, float]] = {}
        for status_cell, cnt, rev in r.all():
            key = str(status_cell).split(".")[-1] if status_cell is not None else ""
            per[key] = (int(cnt or 0), float(rev or 0))
        out: List[dict] = []
        for st in OrderStatus:
            sk = st.value
            c, rv = per.get(sk, (0, 0.0))
            out.append({"status": sk, "count": c, "revenue": rv})
        return out

    async def cancellation_timeseries(
        self,
        db: AsyncSession,
        *,
        from_dt: Optional[datetime] = None,
        to_dt: Optional[datetime] = None,
        group_by: str = "day",
    ) -> List[dict]:
        gb = (group_by or "day").lower()
        if gb == "day":
            end = to_dt or datetime.utcnow()
            end_day = datetime(end.year, end.month, end.day, 23, 59, 59, 999999)
            start_day = datetime(end.year, end.month, end.day) - timedelta(days=13)
            cancelled_cond = Order.status.in_(
                [OrderStatus.CANCELLED, OrderStatus.CANCEL_REQUESTED]
            )
            stmt = (
                select(
                    func.date(Order.order_date).label("period"),
                    func.count(Order.id).label("total_orders"),
                    func.coalesce(func.sum(case((cancelled_cond, 1), else_=0)), 0).label(
                        "cancelled_count"
                    ),
                )
                .where(
                    Order.deleted_at.is_(None),
                    Order.order_date >= start_day,
                    Order.order_date <= end_day,
                )
                .group_by(func.date(Order.order_date))
                .order_by(func.date(Order.order_date))
            )
            result = await db.execute(stmt)
            per: dict[str, tuple[int, int]] = {}
            for period, total_o, cancelled in result.all():
                key = period.isoformat() if hasattr(period, "isoformat") else str(period)
                per[key] = (int(total_o or 0), int(cancelled or 0))

            out: List[dict] = []
            for i in range(14):
                key = (start_day + timedelta(days=i)).date().isoformat()
                tot, canc = per.get(key, (0, 0))
                rate = (canc / tot) if tot else 0.0
                out.append(
                    {
                        "period": key,
                        "total_orders": tot,
                        "cancelled_count": canc,
                        "cancel_rate": round(rate, 4),
                    }
                )
            return out

        if gb == "month":
            period_expr = func.date_format(Order.order_date, "%Y-%m-01")
        elif gb == "week":
            period_expr = func.date_format(Order.order_date, "%X-W%V")
        else:
            period_expr = func.date(Order.order_date)

        cancelled_cond = Order.status.in_(
            [OrderStatus.CANCELLED, OrderStatus.CANCEL_REQUESTED]
        )
        stmt = (
            select(
                period_expr.label("period"),
                func.count(Order.id).label("total_orders"),
                func.coalesce(
                    func.sum(case((cancelled_cond, 1), else_=0)),
                    0,
                ).label("cancelled_count"),
            )
            .where(Order.deleted_at.is_(None))
            .group_by(period_expr)
            .order_by(period_expr)
        )
        if from_dt is not None:
            stmt = stmt.where(Order.order_date >= from_dt)
        if to_dt is not None:
            stmt = stmt.where(Order.order_date <= to_dt)
        result = await db.execute(stmt)
        out: List[dict] = []
        for period, total_o, cancelled in result.all():
            p = period
            if hasattr(p, "isoformat"):
                p = p.isoformat()
            elif p is not None:
                p = str(p)
            else:
                p = ""
            tot = int(total_o or 0)
            canc = int(cancelled or 0)
            rate = (canc / tot) if tot else 0.0
            out.append(
                {
                    "period": p,
                    "total_orders": tot,
                    "cancelled_count": canc,
                    "cancel_rate": round(rate, 4),
                }
            )
        return out


admin_dashboard_service = AdminDashboardService()
