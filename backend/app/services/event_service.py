from typing import Optional, List, Tuple
from datetime import datetime, timezone

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event


async def create_event(
    db: AsyncSession,
    title: str,
    description: Optional[str],
    date: str,
    time: str,
    end_time: Optional[str],
    location: str,
    category: str,
    capacity: int,
    image_url: Optional[str],
    created_by: int,
) -> Event:
    event = Event(
        title=title,
        description=description,
        date=date,
        time=time,
        end_time=end_time,
        location=location,
        category=category,
        capacity=capacity,
        image_url=image_url,
        created_by=created_by,
        registered_count=0,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event


async def get_event(db: AsyncSession, event_id: int) -> Optional[Event]:
    result = await db.execute(select(Event).where(Event.id == event_id))
    return result.scalar_one_or_none()


async def get_events(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 10,
    search: Optional[str] = None,
    category: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    active_only: bool = True,
) -> Tuple[List[Event], int]:
    query = select(Event)
    count_query = select(func.count(Event.id))

    if active_only:
        query = query.where(Event.is_active == True)
        count_query = count_query.where(Event.is_active == True)

    if search:
        search_filter = or_(
            Event.title.ilike(f"%{search}%"),
            Event.description.ilike(f"%{search}%"),
            Event.location.ilike(f"%{search}%"),
        )
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)

    if category:
        query = query.where(Event.category == category)
        count_query = count_query.where(Event.category == category)

    if date_from:
        query = query.where(Event.date >= date_from)
        count_query = count_query.where(Event.date >= date_from)

    if date_to:
        query = query.where(Event.date <= date_to)
        count_query = count_query.where(Event.date <= date_to)

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    offset = (page - 1) * page_size
    query = query.order_by(Event.date.asc(), Event.time.asc()).offset(offset).limit(page_size)

    result = await db.execute(query)
    events = list(result.scalars().all())

    return events, total


async def update_event(
    db: AsyncSession, event_id: int, **kwargs
) -> Optional[Event]:
    event = await get_event(db, event_id)
    if not event:
        return None
    for key, value in kwargs.items():
        if value is not None and hasattr(event, key):
            setattr(event, key, value)
    event.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(event)
    return event


async def delete_event(db: AsyncSession, event_id: int) -> bool:
    event = await get_event(db, event_id)
    if not event:
        return False
    event.is_active = False
    event.updated_at = datetime.now(timezone.utc)
    await db.commit()
    return True
