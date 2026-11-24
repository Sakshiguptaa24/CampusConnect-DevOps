from typing import Optional
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.registration import Registration
from app.models.event import Event
from app.models.user import User


async def verify_qr_code(db: AsyncSession, qr_code: str) -> Optional[dict]:
    """Verify a QR code and return registration details."""
    result = await db.execute(
        select(Registration, Event)
        .join(Event, Registration.event_id == Event.id)
        .where(Registration.qr_code == qr_code)
    )
    row = result.first()
    if not row:
        return None
    reg, event = row
    return {
        "valid": True,
        "registration_id": reg.id,
        "user_id": reg.user_id,
        "event_id": reg.event_id,
        "status": reg.status,
        "event_title": event.title,
        "event_date": event.date,
        "event_time": event.time,
    }


async def mark_attended(db: AsyncSession, qr_code: str) -> dict:
    """Mark a registration as attended via QR code."""
    result = await db.execute(
        select(Registration, Event, User)
        .join(Event, Registration.event_id == Event.id)
        .join(User, Registration.user_id == User.id)
        .where(Registration.qr_code == qr_code)
    )
    row = result.first()
    if not row:
        raise ValueError("Invalid QR code")

    registration, event, user = row

    if registration.status == "attended":
        raise ValueError("Attendance already marked for this registration")

    if registration.status == "cancelled":
        raise ValueError("Registration was cancelled")

    if registration.status == "waitlisted":
        raise ValueError("Registration is on waitlist, not confirmed")

    registration.status = "attended"
    await db.commit()
    await db.refresh(registration)

    return {
        "valid": True,
        "registration_id": registration.id,
        "status": registration.status,
        "message": "Successfully checked in",
        "event_id": event.id,
        "event_title": event.title,
        "student": {
            "name": user.full_name,
            "email": user.email,
        },
        "event": {
            "id": event.id,
            "title": event.title,
            "date": event.date,
            "time": event.time,
        },
    }


async def get_attendance_stats(db: AsyncSession, event_id: int) -> dict:
    """Get attendance statistics for an event."""
    # Total confirmed
    confirmed_result = await db.execute(
        select(func.count(Registration.id)).where(
            and_(
                Registration.event_id == event_id,
                Registration.status.in_(["confirmed", "attended"]),
            )
        )
    )
    total_confirmed = confirmed_result.scalar() or 0

    # Total attended
    attended_result = await db.execute(
        select(func.count(Registration.id)).where(
            and_(
                Registration.event_id == event_id,
                Registration.status == "attended",
            )
        )
    )
    total_attended = attended_result.scalar() or 0

    # Total waitlisted
    waitlisted_result = await db.execute(
        select(func.count(Registration.id)).where(
            and_(
                Registration.event_id == event_id,
                Registration.status == "waitlisted",
            )
        )
    )
    total_waitlisted = waitlisted_result.scalar() or 0

    # Total cancelled
    cancelled_result = await db.execute(
        select(func.count(Registration.id)).where(
            and_(
                Registration.event_id == event_id,
                Registration.status == "cancelled",
            )
        )
    )
    total_cancelled = cancelled_result.scalar() or 0

    attendance_rate = (total_attended / total_confirmed * 100) if total_confirmed > 0 else 0

    return {
        "event_id": event_id,
        "total_confirmed": total_confirmed,
        "total_attended": total_attended,
        "attended_count": total_attended,
        "total_waitlisted": total_waitlisted,
        "total_cancelled": total_cancelled,
        "attendance_rate": round(attendance_rate, 2),
    }
