from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from app.core.database import Base


class Registration(Base):
    __tablename__ = "registrations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False, index=True)
    status = Column(String(20), nullable=False, default="confirmed")  # confirmed, waitlisted, cancelled, attended
    qr_code = Column(String(100), unique=True, nullable=False, index=True)
    registered_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    cancelled_at = Column(DateTime, nullable=True)
    waitlist_position = Column(Integer, nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "event_id",
            name="uq_active_registration",
        ),
    )
