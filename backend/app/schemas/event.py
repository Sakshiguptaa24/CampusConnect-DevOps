from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class EventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    date: str  # YYYY-MM-DD
    time: str  # HH:MM
    end_time: Optional[str] = None
    location: str
    category: str
    capacity: int = 100
    image_url: Optional[str] = None


class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    end_time: Optional[str] = None
    location: Optional[str] = None
    category: Optional[str] = None
    capacity: Optional[int] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None


class EventResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    date: str
    time: str
    end_time: Optional[str] = None
    location: str
    category: str
    capacity: int
    registered_count: int
    image_url: Optional[str] = None
    is_active: bool
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EventList(BaseModel):
    events: List[EventResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
