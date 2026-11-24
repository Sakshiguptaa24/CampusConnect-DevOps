from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_admin
from app.services import analytics_service

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/dashboard")
async def get_dashboard_stats(
    current_user=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    stats = await analytics_service.get_dashboard_stats(db)
    return stats


@router.get("/events/{event_id}")
async def get_event_analytics(
    event_id: int,
    current_user=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    analytics = await analytics_service.get_event_analytics(db, event_id)
    if not analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )
    return analytics


@router.get("/categories")
async def get_category_stats(
    current_user=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    stats = await analytics_service.get_category_stats(db)
    return stats


@router.get("/trends")
async def get_registration_trends(
    current_user=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    trends = await analytics_service.get_registration_trends(db)
    return trends
