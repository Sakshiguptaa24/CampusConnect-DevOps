from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event
from app.models.registration import Registration
from app.models.user import User


async def get_dashboard_stats(db: AsyncSession) -> dict:
    """Get overall dashboard statistics."""
    # Total events
    total_events_result = await db.execute(select(func.count(Event.id)).where(Event.is_active == True))
    total_events = total_events_result.scalar() or 0

    # Total users
    total_users_result = await db.execute(select(func.count(User.id)).where(User.is_active == True))
    total_users = total_users_result.scalar() or 0

    # Total registrations (non-cancelled)
    total_registrations_result = await db.execute(
        select(func.count(Registration.id)).where(Registration.status.notin_(["cancelled"]))
    )
    total_registrations = total_registrations_result.scalar() or 0

    # Total attended
    total_attended_result = await db.execute(
        select(func.count(Registration.id)).where(Registration.status == "attended")
    )
    total_attended = total_attended_result.scalar() or 0

    # Overall attendance rate
    confirmed_plus_attended_result = await db.execute(
        select(func.count(Registration.id)).where(Registration.status.in_(["confirmed", "attended"]))
    )
    confirmed_plus_attended = confirmed_plus_attended_result.scalar() or 0
    attendance_rate = (total_attended / confirmed_plus_attended * 100) if confirmed_plus_attended > 0 else 0

    return {
        "total_events": total_events,
        "total_users": total_users,
        "total_registrations": total_registrations,
        "total_attended": total_attended,
        "attendance_rate": round(attendance_rate, 2),
    }


async def get_event_analytics(db: AsyncSession, event_id: int) -> dict:
    """Get analytics for a specific event."""
    event_result = await db.execute(select(Event).where(Event.id == event_id))
    event = event_result.scalar_one_or_none()
    if not event:
        return {}

    # Registration counts by status
    status_counts_result = await db.execute(
        select(Registration.status, func.count(Registration.id))
        .where(Registration.event_id == event_id)
        .group_by(Registration.status)
    )
    status_counts = {row[0]: row[1] for row in status_counts_result.all()}

    confirmed = status_counts.get("confirmed", 0)
    attended = status_counts.get("attended", 0)
    waitlisted = status_counts.get("waitlisted", 0)
    cancelled = status_counts.get("cancelled", 0)

    fill_rate = (event.registered_count / event.capacity * 100) if event.capacity > 0 else 0
    attendance_rate = (attended / (confirmed + attended) * 100) if (confirmed + attended) > 0 else 0

    return {
        "event_id": event.id,
        "event_title": event.title,
        "capacity": event.capacity,
        "registered_count": event.registered_count,
        "confirmed": confirmed,
        "attended": attended,
        "waitlisted": waitlisted,
        "cancelled": cancelled,
        "fill_rate": round(fill_rate, 2),
        "attendance_rate": round(attendance_rate, 2),
    }


async def get_category_stats(db: AsyncSession) -> list:
    """Get statistics grouped by event category."""
    result = await db.execute(
        select(
            Event.category,
            func.count(Event.id).label("event_count"),
            func.sum(Event.registered_count).label("total_registrations"),
            func.sum(Event.capacity).label("total_capacity"),
        )
        .where(Event.is_active == True)
        .group_by(Event.category)
        .order_by(func.count(Event.id).desc())
    )
    rows = result.all()
    categories = []
    for row in rows:
        total_cap = row.total_capacity or 1
        total_reg = row.total_registrations or 0
        categories.append(
            {
                "category": row.category,
                "event_count": row.event_count,
                "total_registrations": total_reg,
                "total_capacity": row.total_capacity or 0,
                "fill_rate": round(total_reg / total_cap * 100, 2),
            }
        )
    return categories


async def get_registration_trends(db: AsyncSession) -> list:
    """Get registration trends over time."""
    result = await db.execute(
        select(
            func.date(Registration.registered_at).label("date"),
            func.count(Registration.id).label("count"),
        )
        .where(Registration.status.notin_(["cancelled"]))
        .group_by(func.date(Registration.registered_at))
        .order_by(func.date(Registration.registered_at).asc())
    )
    rows = result.all()
    return [{"date": str(row.date), "count": row.count} for row in rows]
