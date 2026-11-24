from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, get_current_admin
from app.models.user import User
from app.schemas.registration import (
    RegistrationCreate,
    RegistrationResponse,
    RegistrationWithEvent,
    RegistrationWithUser,
)
from app.services import registration_service
from app.utils.qr_generator import generate_qr_code

router = APIRouter(prefix="/api/registrations", tags=["registrations"])


@router.post("", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED)
async def register_for_event(
    reg_data: RegistrationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        registration = await registration_service.register_for_event(
            db, user_id=current_user.id, event_id=reg_data.event_id
        )
        return registration
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{event_id}", response_model=RegistrationResponse)
async def cancel_registration(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    registration = await registration_service.cancel_registration(db, user_id=current_user.id, event_id=event_id)
    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found",
        )
    return registration


@router.get("/my", response_model=List[RegistrationWithEvent])
async def get_my_registrations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    registrations = await registration_service.get_user_registrations(db, user_id=current_user.id)
    return registrations


@router.get("/event/{event_id}/participants", response_model=List[RegistrationWithUser])
async def get_event_participants(
    event_id: int,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    participants = await registration_service.get_event_participants(db, event_id)
    return participants


@router.get("/{registration_id}/qr")
async def get_registration_qr(
    registration_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select
    from app.models.registration import Registration

    result = await db.execute(select(Registration).where(Registration.id == registration_id))
    registration = result.scalar_one_or_none()
    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found",
        )
    if registration.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this QR code",
        )
    qr_data_uri = generate_qr_code(registration.qr_code)
    return {"qr_code": registration.qr_code, "qr_image": qr_data_uri}
