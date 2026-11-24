import uuid
from typing import Optional, List
from datetime import datetime, timezone

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.registration import Registration
from app.models.event import Event
from app.models.user import User


async def register_for_event(
    db: AsyncSession, user_id: int, event_id: int
) -> Registration:
    """Register a user for an event. Waitlist if at capacity."""
    # Check event exists and is active
    event_result = await db.execute(select(Event).where(Event.id == event_id))
    event = event_result.scalar_one_or_none()
    if not event:
        raise ValueError("Event not found")
    if not event.is_active:
        raise ValueError("Event is no longer active")

    # Check for existing active registration (not cancelled)
    existing_result = await db.execute(
        select(Registration).where(
            and_(
                Registration.user_id == user_id,
                Registration.event_id == event_id,
                Registration.status.notin_(["cancelled"]),
            )
        )
    )
    existing = existing_result.scalar_one_or_none()
    if existing:
        raise ValueError("Already registered for this event")

    # Determine status based on capacity
    qr_code = str(uuid.uuid4())

    if event.registered_count < event.capacity:
        status = "confirmed"
        event.registered_count += 1
        waitlist_position = None
    else:
        status = "waitlisted"
        # Get next waitlist position
        max_pos_result = await db.execute(
            select(func.max(Registration.waitlist_position)).where(
                and_(
                    Registration.event_id == event_id,
                    Registration.status == "waitlisted",
                )
            )
        )
        max_pos = max_pos_result.scalar()
        waitlist_position = (max_pos or 0) + 1

    # Check if previously cancelled, can reactivate
    cancelled_result = await db.execute(
        select(Registration).where(
            and_(
                Registration.user_id == user_id,
                Registration.event_id == event_id,
                Registration.status == "cancelled",
            )
        )
    )
    cancelled_reg = cancelled_result.scalar_one_or_none()
    if cancelled_reg:
        cancelled_reg.status = status
        cancelled_reg.qr_code = qr_code
        cancelled_reg.registered_at = datetime.now(timezone.utc)
        cancelled_reg.cancelled_at = None
        cancelled_reg.waitlist_position = waitlist_position
        await db.commit()
        await db.refresh(cancelled_reg)
        return cancelled_reg

    registration = Registration(
        user_id=user_id,
        event_id=event_id,
        status=status,
        qr_code=qr_code,
        registered_at=datetime.now(timezone.utc),
        waitlist_position=waitlist_position,
    )
    db.add(registration)
    await db.commit()
    await db.refresh(registration)
    return registration


async def cancel_registration(
    db: AsyncSession, user_id: int, event_id: int
) -> Optional[Registration]:
    """Cancel a registration and promote from waitlist if applicable."""
    result = await db.execute(
        select(Registration).where(
            and_(
                Registration.user_id == user_id,
                Registration.event_id == event_id,
                Registration.status.in_(["confirmed", "waitlisted"]),
            )
        )
    )
    registration = result.scalar_one_or_none()
    if not registration:
        return None

    was_confirmed = registration.status == "confirmed"
    registration.status = "cancelled"
    registration.cancelled_at = datetime.now(timezone.utc)

    # If was confirmed, decrement count and promote waitlisted
    if was_confirmed:
        event_result = await db.execute(select(Event).where(Event.id == event_id))
        event = event_result.scalar_one_or_none()
        if event and event.registered_count > 0:
            event.registered_count -= 1

            # Promote first waitlisted person
            waitlisted_result = await db.execute(
                select(Registration)
                .where(
                    and_(
                        Registration.event_id == event_id,
                        Registration.status == "waitlisted",
                    )
                )
                .order_by(Registration.waitlist_position.asc())
                .limit(1)
            )
            next_in_line = waitlisted_result.scalar_one_or_none()
            if next_in_line:
                next_in_line.status = "confirmed"
                next_in_line.waitlist_position = None
                event.registered_count += 1

    await db.commit()
    await db.refresh(registration)
    return registration


async def get_user_registrations(
    db: AsyncSession, user_id: int
) -> List[dict]:
    """Get all registrations for a user with event details."""
    result = await db.execute(
        select(Registration, Event)
        .join(Event, Registration.event_id == Event.id)
        .where(Registration.user_id == user_id)
        .order_by(Registration.registered_at.desc())
    )
    rows = result.all()
    registrations = []
    for reg, event in rows:
        registrations.append({
            "id": reg.id,
            "user_id": reg.user_id,
            "event_id": reg.event_id,
            "status": reg.status,
            "qr_code": reg.qr_code,
            "registered_at": reg.registered_at,
            "cancelled_at": reg.cancelled_at,
            "waitlist_position": reg.waitlist_position,
            "event_title": event.title,
            "event_date": event.date,
            "event_time": event.time,
            "event_location": event.location,
            "event_category": event.category,
        })
    return registrations


async def get_event_participants(
    db: AsyncSession, event_id: int
) -> List[dict]:
    """Get all participants for an event with user details."""
    result = await db.execute(
        select(Registration, User)
        .join(User, Registration.user_id == User.id)
        .where(Registration.event_id == event_id)
        .order_by(Registration.registered_at.asc())
    )
    rows = result.all()
    participants = []
    for reg, user in rows:
        participants.append({
            "id": reg.id,
            "user_id": reg.user_id,
            "event_id": reg.event_id,
            "status": reg.status,
            "qr_code": reg.qr_code,
            "registered_at": reg.registered_at,
            "cancelled_at": reg.cancelled_at,
            "waitlist_position": reg.waitlist_position,
            "user_name": user.full_name,
            "user_email": user.email,
            "user_department": user.department,
        })
    return participants
