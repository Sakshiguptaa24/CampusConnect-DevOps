from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class RegistrationCreate(BaseModel):
    event_id: int


class RegistrationResponse(BaseModel):
    id: int
    user_id: int
    event_id: int
    status: str
    qr_code: str
    registered_at: datetime
    cancelled_at: Optional[datetime] = None
    waitlist_position: Optional[int] = None

    model_config = {"from_attributes": True}


class AttendanceVerify(BaseModel):
    qr_code: str


class RegistrationWithEvent(BaseModel):
    id: int
    user_id: int
    event_id: int
    status: str
    qr_code: str
    registered_at: datetime
    cancelled_at: Optional[datetime] = None
    waitlist_position: Optional[int] = None
    event_title: Optional[str] = None
    event_date: Optional[str] = None
    event_time: Optional[str] = None
    event_location: Optional[str] = None
    event_category: Optional[str] = None

    model_config = {"from_attributes": True}


class RegistrationWithUser(BaseModel):
    id: int
    user_id: int
    event_id: int
    status: str
    qr_code: str
    registered_at: datetime
    cancelled_at: Optional[datetime] = None
    waitlist_position: Optional[int] = None
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    user_department: Optional[str] = None

    model_config = {"from_attributes": True}
