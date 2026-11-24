import logging
import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import User
from app.models.event import Event
from app.models.registration import Registration

logger = logging.getLogger("campusconnect.seed")


async def seed_database(db: AsyncSession):
    """Seed demo users, events, and sample registrations if not already present."""
    # Check if admin already exists
    admin_query = await db.execute(select(User).where(User.email == settings.ADMIN_EMAIL))
    if admin_query.scalar_one_or_none():
        logger.info("Database already seeded. Skipping seed process.")
        return

    logger.info("Seeding initial database demo data...")

    # 1. Create Admin User
    admin = User(
        email=settings.ADMIN_EMAIL,
        full_name="System Administrator",
        hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
        is_admin=True,
        is_active=True,
        department="Administration",
        phone="+1 555-0100",
        created_at=datetime.now(timezone.utc),
    )
    db.add(admin)

    # 2. Create Demo Student
    student = User(
        email="student@campusconnect.com",
        full_name="Alex Johnson",
        hashed_password=get_password_hash("Student@123"),
        is_admin=False,
        is_active=True,
        department="Computer Science & Engineering",
        phone="+1 555-0101",
        created_at=datetime.now(timezone.utc),
    )
    db.add(student)

    # Additional Demo Students
    student2 = User(
        email="sarah.chen@campusconnect.com",
        full_name="Sarah Chen",
        hashed_password=get_password_hash("Student@123"),
        is_admin=False,
        is_active=True,
        department="Information Technology",
        phone="+1 555-0102",
        created_at=datetime.now(timezone.utc),
    )
    student3 = User(
        email="rahul.sharma@campusconnect.com",
        full_name="Rahul Sharma",
        hashed_password=get_password_hash("Student@123"),
        is_admin=False,
        is_active=True,
        department="Mechanical Engineering",
        phone="+1 555-0103",
        created_at=datetime.now(timezone.utc),
    )
    db.add_all([student2, student3])
    await db.flush()

    # 3. Create Events
    now = datetime.now(timezone.utc)
    events_data = [
        {
            "title": "AI & Cloud Tech Summit 2026",
            "description": "Explore cutting-edge advancements in generative AI, distributed cloud systems, and scalable infrastructure with industry pioneers from Google, AWS, and leading startups. Includes hands-on demo sessions.",
            "date": (now + timedelta(days=5)).strftime("%Y-%m-%d"),
            "time": "09:30",
            "end_time": "17:00",
            "location": "Main Auditorium, Science Block",
            "category": "Technology",
            "capacity": 50,
            "registered_count": 3,
            "image_url": "https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800&auto=format&fit=crop&q=80",
            "is_active": True,
            "created_by": admin.id,
        },
        {
            "title": "Campus Hackathon 24H: HackTheFuture",
            "description": "24-hour sprint to build AI-driven solutions addressing university and sustainability challenges. Meals, energy drinks, and mentor support provided throughout.",
            "date": (now + timedelta(days=12)).strftime("%Y-%m-%d"),
            "time": "10:00",
            "end_time": "10:00",
            "location": "Innovation Hub, 3rd Floor",
            "category": "Technology",
            "capacity": 2,  # Intentionally small to demo waitlist!
            "registered_count": 2,
            "image_url": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=800&auto=format&fit=crop&q=80",
            "is_active": True,
            "created_by": admin.id,
        },
        {
            "title": "Annual Cultural Fest - Resonance 2026",
            "description": "The largest collegiate cultural extravaganza featuring live music battles, inter-college choreography showdowns, dramatic performances, and gourmet street food stalls.",
            "date": (now + timedelta(days=18)).strftime("%Y-%m-%d"),
            "time": "16:00",
            "end_time": "22:00",
            "location": "Central Open Amphitheatre",
            "category": "Cultural",
            "capacity": 200,
            "registered_count": 2,
            "image_url": "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?w=800&auto=format&fit=crop&q=80",
            "is_active": True,
            "created_by": admin.id,
        },
        {
            "title": "Inter-College Football Championship",
            "description": "Annual knockout soccer tournament featuring top collegiate teams. Cheer for the home team in the opening clash under stadium floodlights.",
            "date": (now + timedelta(days=7)).strftime("%Y-%m-%d"),
            "time": "15:00",
            "end_time": "19:00",
            "location": "University Sports Arena",
            "category": "Sports",
            "capacity": 100,
            "registered_count": 1,
            "image_url": "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?w=800&auto=format&fit=crop&q=80",
            "is_active": True,
            "created_by": admin.id,
        },
        {
            "title": "Design Systems & Modern UI/UX Masterclass",
            "description": "A deep dive into building enterprise-grade design systems with Figma and Tailwind CSS. Learn atomic design, accessibility tokens, and animation choreography.",
            "date": (now + timedelta(days=9)).strftime("%Y-%m-%d"),
            "time": "14:00",
            "end_time": "17:30",
            "location": "Design Lab 2B, Arts Building",
            "category": "Workshop",
            "capacity": 30,
            "registered_count": 2,
            "image_url": "https://images.unsplash.com/photo-1581291518857-4e27b48ff24e?w=800&auto=format&fit=crop&q=80",
            "is_active": True,
            "created_by": admin.id,
        },
        {
            "title": "Career Fair & Tech Talent Networking",
            "description": "Connect directly with technical recruiters and engineering managers from Fortune 500 enterprises, tech unicorns, and research labs. Bring updated resumes.",
            "date": (now + timedelta(days=22)).strftime("%Y-%m-%d"),
            "time": "10:00",
            "end_time": "16:00",
            "location": "Convention Center Hall A",
            "category": "Seminar",
            "capacity": 150,
            "registered_count": 1,
            "image_url": "https://images.unsplash.com/photo-1515187029135-18ee286d815b?w=800&auto=format&fit=crop&q=80",
            "is_active": True,
            "created_by": admin.id,
        },
        {
            "title": "Sunset Acoustic Jam & Open Mic",
            "description": "An intimate evening of acoustic melodies, spoken word poetry, and indie performances under the campus pines. Complimentary coffee and hot cocoa.",
            "date": (now + timedelta(days=14)).strftime("%Y-%m-%d"),
            "time": "18:00",
            "end_time": "21:00",
            "location": "Student Commons Lawn",
            "category": "Cultural",
            "capacity": 60,
            "registered_count": 1,
            "image_url": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=800&auto=format&fit=crop&q=80",
            "is_active": True,
            "created_by": admin.id,
        },
        {
            "title": "Zero-Day Defense: Cybersecurity CTF",
            "description": "Capture the Flag tournament testing binary exploitation, reverse engineering, web penetration, and cryptography. Suitable for intermediate and advanced security enthusiasts.",
            "date": (now + timedelta(days=28)).strftime("%Y-%m-%d"),
            "time": "11:00",
            "end_time": "18:00",
            "location": "Cyber Forensics Lab, Room 404",
            "category": "Technology",
            "capacity": 40,
            "registered_count": 1,
            "image_url": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800&auto=format&fit=crop&q=80",
            "is_active": True,
            "created_by": admin.id,
        },
    ]

    created_events = []
    for edata in events_data:
        event = Event(**edata)
        db.add(event)
        created_events.append(event)

    await db.flush()

    # 4. Create Initial Registrations with QR Codes
    ev_tech = created_events[0]
    ev_hack = created_events[1]  # Capacity 2
    ev_fest = created_events[2]
    ev_workshop = created_events[4]

    # Fill Hackathon (Capacity 2):
    # Student 2 is confirmed
    # Student 3 is confirmed
    # Alex Johnson (student) is waitlisted (waitlist_position = 1)
    hack_reg1 = Registration(
        user_id=student2.id,
        event_id=ev_hack.id,
        status="confirmed",
        qr_code=str(uuid.uuid4()),
        registered_at=now - timedelta(hours=3),
        waitlist_position=None,
    )
    hack_reg2 = Registration(
        user_id=student3.id,
        event_id=ev_hack.id,
        status="confirmed",
        qr_code=str(uuid.uuid4()),
        registered_at=now - timedelta(hours=2),
        waitlist_position=None,
    )
    hack_reg3 = Registration(
        user_id=student.id,
        event_id=ev_hack.id,
        status="waitlisted",
        qr_code=str(uuid.uuid4()),
        registered_at=now - timedelta(hours=1),
        waitlist_position=1,
    )

    # Tech Summit (Confirmed for Alex and Sarah)
    tech_reg1 = Registration(
        user_id=student.id,
        event_id=ev_tech.id,
        status="confirmed",
        qr_code=str(uuid.uuid4()),
        registered_at=now - timedelta(days=1),
        waitlist_position=None,
    )
    tech_reg2 = Registration(
        user_id=student2.id,
        event_id=ev_tech.id,
        status="confirmed",
        qr_code=str(uuid.uuid4()),
        registered_at=now - timedelta(days=1),
        waitlist_position=None,
    )

    # Cultural Fest (Confirmed for Alex)
    fest_reg = Registration(
        user_id=student.id,
        event_id=ev_fest.id,
        status="confirmed",
        qr_code=str(uuid.uuid4()),
        registered_at=now - timedelta(days=2),
        waitlist_position=None,
    )

    # UI/UX Workshop (Attended for Alex - testing attendance check-in)
    workshop_reg = Registration(
        user_id=student.id,
        event_id=ev_workshop.id,
        status="attended",
        qr_code=str(uuid.uuid4()),
        registered_at=now - timedelta(days=3),
        waitlist_position=None,
    )

    db.add_all([hack_reg1, hack_reg2, hack_reg3, tech_reg1, tech_reg2, fest_reg, workshop_reg])
    await db.commit()
    logger.info("Database seeding successfully completed.")
