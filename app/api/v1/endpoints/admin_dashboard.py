"""Dashboard / analytics admin."""
import csv
import io
from datetime import date, datetime, time
from typing import Literal, Optional

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_superuser
from app.core.database import get_db
from app.models.user import User
from app.schemas.admin_dashboard import (
    CancelRatePointOut,
    CategoryRevenueRow,
    DashboardSummaryOut,
    OrderStatusBreakdownRow,
    TopBookRow,
    TopCustomerOut,
    UserTimeseriesRow,
    RevenueTimeseriesRow,
)
from app.services.admin_dashboard_service import admin_dashboard_service
from app.services.audit_service import record_admin_audit
from app.services.order_service import order_service

router = APIRouter(prefix="/dashboard", tags=["admin-dashboard"])


def _range(from_d: Optional[date], to_d: Optional[date]) -> tuple[Optional[datetime], Optional[datetime]]:
    from_dt = datetime.combine(from_d, time.min) if from_d else None
    to_dt = datetime.combine(to_d, time.max) if to_d else None
    return from_dt, to_dt


@router.get("/summary", response_model=DashboardSummaryOut)
async def dashboard_summary(
    from_d: Optional[date] = Query(None, alias="from"),
    to_d: Optional[date] = Query(None, alias="to"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    from_dt, to_dt = _range(from_d, to_d)
    data = await admin_dashboard_service.summary(db, from_dt=from_dt, to_dt=to_dt)
    return DashboardSummaryOut.model_validate(data)


@router.get("/top-books", response_model=list[TopBookRow])
async def dashboard_top_books(
    from_d: Optional[date] = Query(None, alias="from"),
    to_d: Optional[date] = Query(None, alias="to"),
    limit: int = Query(10, ge=1, le=50),
    metric: Literal["revenue", "quantity"] = Query("revenue"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    from_dt, to_dt = _range(from_d, to_d)
    rows = await admin_dashboard_service.top_books(
        db, from_dt=from_dt, to_dt=to_dt, limit=limit, metric=metric
    )
    return [TopBookRow.model_validate(r) for r in rows]


@router.get("/by-category", response_model=list[CategoryRevenueRow])
async def dashboard_by_category(
    from_d: Optional[date] = Query(None, alias="from"),
    to_d: Optional[date] = Query(None, alias="to"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    from_dt, to_dt = _range(from_d, to_d)
    rows = await admin_dashboard_service.revenue_by_category(
        db, from_dt=from_dt, to_dt=to_dt
    )
    return [CategoryRevenueRow.model_validate(r) for r in rows]


@router.get("/revenue.csv")
async def dashboard_revenue_csv(
    from_d: Optional[date] = Query(None, alias="from"),
    to_d: Optional[date] = Query(None, alias="to"),
    group_by: Literal["day", "week", "month"] = Query("day"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    from_dt, to_dt = _range(from_d, to_d)
    rows = await order_service.get_revenue_timeseries(
        db, from_dt=from_dt, to_dt=to_dt, group_by=group_by
    )
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["period", "order_count", "revenue"])
    for r in rows:
        w.writerow([r["period"], r["order_count"], r["revenue"]])
    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="revenue_timeseries.csv"'},
    )


@router.get("/revenue-timeseries", response_model=list[RevenueTimeseriesRow])
async def dashboard_revenue_timeseries(
    from_d: Optional[date] = Query(None, alias="from"),
    to_d: Optional[date] = Query(None, alias="to"),
    group_by: Literal["day", "week", "month"] = Query("day"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    from_dt, to_dt = _range(from_d, to_d)
    rows = await order_service.get_revenue_timeseries(
        db, from_dt=from_dt, to_dt=to_dt, group_by=group_by
    )
    return [RevenueTimeseriesRow.model_validate(r) for r in rows]



@router.get("/user-timeseries", response_model=list[UserTimeseriesRow])
async def dashboard_user_timeseries(
    from_d: Optional[date] = Query(None, alias="from"),
    to_d: Optional[date] = Query(None, alias="to"),
    group_by: Literal["day", "week", "month"] = Query("day"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    from_dt, to_dt = _range(from_d, to_d)
    rows = await admin_dashboard_service.user_timeseries(
        db, from_dt=from_dt, to_dt=to_dt, group_by=group_by
    )
    return [UserTimeseriesRow.model_validate(r) for r in rows]


@router.get("/top-customers", response_model=list[TopCustomerOut])
async def dashboard_top_customers(
    request: Request,
    from_d: Optional[date] = Query(None, alias="from"),
    to_d: Optional[date] = Query(None, alias="to"),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    from_dt, to_dt = _range(from_d, to_d)
    rows = await admin_dashboard_service.get_top_customers(
        db, from_dt=from_dt, to_dt=to_dt, limit=limit
    )
    await record_admin_audit(
        db,
        actor_user_id=current_user.id,
        action="admin.dashboard.view.top_customers",
        target_type="dashboard",
        payload={"from": str(from_d), "to": str(to_d), "limit": limit},
        ip=request.client.host if request.client else None,
    )
    return [TopCustomerOut.model_validate(r) for r in rows]


@router.get("/order-status-breakdown", response_model=list[OrderStatusBreakdownRow])
async def dashboard_order_status_breakdown(
    request: Request,
    from_d: Optional[date] = Query(None, alias="from"),
    to_d: Optional[date] = Query(None, alias="to"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    from_dt, to_dt = _range(from_d, to_d)
    rows = await admin_dashboard_service.order_status_breakdown(
        db, from_dt=from_dt, to_dt=to_dt
    )
    await record_admin_audit(
        db,
        actor_user_id=current_user.id,
        action="admin.dashboard.view.order_status_breakdown",
        target_type="dashboard",
        payload={"from": str(from_d), "to": str(to_d)},
        ip=request.client.host if request.client else None,
    )
    return [OrderStatusBreakdownRow.model_validate(r) for r in rows]


@router.get("/cancellation-timeseries", response_model=list[CancelRatePointOut])
async def dashboard_cancellation_timeseries(
    request: Request,
    from_d: Optional[date] = Query(None, alias="from"),
    to_d: Optional[date] = Query(None, alias="to"),
    group_by: Literal["day", "week", "month"] = Query("day"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    from_dt, to_dt = _range(from_d, to_d)
    rows = await admin_dashboard_service.cancellation_timeseries(
        db, from_dt=from_dt, to_dt=to_dt, group_by=group_by
    )
    await record_admin_audit(
        db,
        actor_user_id=current_user.id,
        action="admin.dashboard.view.cancellation_timeseries",
        target_type="dashboard",
        payload={
            "from": str(from_d),
            "to": str(to_d),
            "group_by": group_by,
        },
        ip=request.client.host if request.client else None,
    )
    return [CancelRatePointOut.model_validate(r) for r in rows]
