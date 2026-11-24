from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, get_current_admin
from app.schemas.registration import AttendanceVerify
from app.services import attendance_service

router = APIRouter(prefix="/api/attendance", tags=["attendance"])


@router.post("/verify")
async def verify_attendance(
    data: AttendanceVerify,
    current_user=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await attendance_service.mark_attended(db, qr_code=data.qr_code)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/verify/{qr_code}")
async def lookup_qr(
    qr_code: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    info = await attendance_service.verify_qr_code(db, qr_code=qr_code)
    if not info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid QR code",
        )
    return info


@router.get("/stats/{event_id}")
async def get_attendance_stats(
    event_id: int,
    current_user=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    stats = await attendance_service.get_attendance_stats(db, event_id=event_id)
    return stats
