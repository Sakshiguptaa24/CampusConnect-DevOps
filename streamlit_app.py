import asyncio
import base64
import io
import os
import sys
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from PIL import Image
import plotly.express as px
import qrcode
import streamlit as st

# Configure page settings
st.set_page_config(
    page_title="CampusConnect — Smart Event Hub",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Ensure backend directory is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# Set database path to backend/campusconnect.db or default
DB_PATH = os.path.join(BACKEND_DIR, "campusconnect.db")
os.environ.setdefault("DATABASE_URL", f"sqlite+aiosqlite:///{DB_PATH}")

from app.core.database import async_session_maker, create_all_tables, engine, Base
from app.core.security import verify_password, get_password_hash
from app.core.seed import seed_database
from app.models.user import User
from app.models.event import Event
from app.models.registration import Registration
from app.services import (
    event_service,
    registration_service,
    attendance_service,
    analytics_service,
)
from app.utils.csv_export import export_registrations_csv, export_attendees_csv
from sqlalchemy import select, func

# Try importing OpenCV for QR code detection
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False


# -------------------------------------------------------------
# ASYNC EXECUTION HELPER
# -------------------------------------------------------------
def run_async(coro):
    """Run an async coroutine synchronously inside Streamlit's thread."""
    return asyncio.run(coro)


# -------------------------------------------------------------
# DATABASE INITIALIZATION
# -------------------------------------------------------------
@st.cache_resource
def initialize_database():
    """Ensure database schema is created and initial data is seeded."""
    async def _init():
        await create_all_tables()
        async with async_session_maker() as db:
            result = await db.execute(select(func.count(User.id)))
            user_count = result.scalar() or 0
            if user_count == 0:
                await seed_database(db)
    run_async(_init())
    return True

initialize_database()


def reset_database_action():
    """Wipe and re-seed the demo database to fresh pristine state."""
    async def _reset():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        async with async_session_maker() as db:
            await seed_database(db)
    run_async(_reset())


# -------------------------------------------------------------
# QR CODE UTILITIES
# -------------------------------------------------------------
def make_qr_image(data_str: str) -> Image.Image:
    """Generate PIL Image QR code from payload string."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=3,
    )
    qr.add_data(data_str)
    qr.make(fit=True)
    return qr.make_image(fill_color="#1E1B4B", back_color="#FFFFFF").convert("RGB")


def decode_qr_image(image_bytes: bytes) -> str | None:
    """Decode a QR code payload from uploaded image bytes using OpenCV."""
    if not OPENCV_AVAILABLE:
        return None
    try:
        pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        np_img = np.array(pil_img)
        # OpenCV uses BGR format
        cv_img = cv2.cvtColor(np_img, cv2.COLOR_RGB2BGR)
        detector = cv2.QRCodeDetector()
        data, _, _ = detector.detectAndDecode(cv_img)
        return data if data else None
    except Exception:
        return None


# -------------------------------------------------------------
# CUSTOM RESPONSIVE CSS
# -------------------------------------------------------------
st.markdown("""
<style>
    /* Global Styling */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
    }
    
    /* Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, #4338CA 0%, #6366F1 50%, #7C3AED 100%);
        color: white;
        padding: 2.2rem 2rem;
        border-radius: 1rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 25px -5px rgba(79, 70, 229, 0.25);
    }
    .hero-title {
        font-size: 2rem;
        font-weight: 800;
        margin: 0;
        color: #FFFFFF;
        letter-spacing: -0.025em;
    }
    .hero-subtitle {
        font-size: 1.05rem;
        opacity: 0.92;
        margin-top: 0.5rem;
        margin-bottom: 0;
        color: #E0E7FF;
        line-height: 1.5;
    }

    /* Demo Sandbox Notice */
    .sandbox-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.18);
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 0.35rem 0.85rem;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
        color: #F8FAFC;
    }

    /* Event Card */
    .event-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 0.875rem;
        padding: 1.4rem;
        margin-bottom: 1rem;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.03);
    }
    .event-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 20px -8px rgba(0, 0, 0, 0.08);
        border-color: #CBD5E1;
    }

    /* Ticket Pass */
    .ticket-container {
        background: #FFFFFF;
        border: 2px dashed #CBD5E1;
        border-radius: 1rem;
        padding: 1.5rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }

    /* Badges */
    .badge-confirmed {
        background: #DEF7EC;
        color: #03543F;
        padding: 0.25rem 0.7rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 700;
        display: inline-block;
    }
    .badge-waitlisted {
        background: #FEF3C7;
        color: #92400E;
        padding: 0.25rem 0.7rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 700;
        display: inline-block;
    }
    .badge-attended {
        background: #E0E7FF;
        color: #3730A3;
        padding: 0.25rem 0.7rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 700;
        display: inline-block;
    }
    .badge-cancelled {
        background: #F1F5F9;
        color: #64748B;
        padding: 0.25rem 0.7rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 700;
        display: inline-block;
    }

    /* Metric Highlight */
    .metric-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 0.75rem;
        padding: 1.1rem;
        text-align: center;
    }
    .metric-value {
        font-size: 1.85rem;
        font-weight: 800;
        color: #312E81;
    }
    .metric-label {
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.25rem;
    }

    /* Mobile adjustments */
    @media (max-width: 768px) {
        .hero-title { font-size: 1.5rem; }
        .hero-banner { padding: 1.5rem 1.25rem; }
        .metric-value { font-size: 1.4rem; }
    }
</style>
""", unsafe_allow_html=True)


# -------------------------------------------------------------
# SESSION STATE INITIALIZATION
# -------------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None
if "role" not in st.session_state:
    st.session_state.role = None
if "recent_scans" not in st.session_state:
    st.session_state.recent_scans = []


def login_action(user_dict: dict):
    st.session_state.authenticated = True
    st.session_state.user = user_dict
    st.session_state.role = "admin" if user_dict["is_admin"] else "student"


def logout_action():
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.role = None
    st.rerun()


# -------------------------------------------------------------
# SIDEBAR
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🎓 **CampusConnect**")
    st.caption("Smart College Event & Attendance Hub")
    st.markdown("---")

    if st.session_state.authenticated and st.session_state.user:
        user = st.session_state.user
        role_label = "🛡️ Administrator" if user["is_admin"] else "🎓 Student"
        st.markdown(f"**Signed in as:**")
        st.markdown(f"**{user['full_name']}**")
        st.caption(f"{user['email']} • {role_label}")
        
        if user.get("department"):
            st.caption(f"Dept: {user['department']}")
        
        st.markdown("---")
        
        # Navigation Options based on Role
        if user["is_admin"]:
            page = st.radio(
                "Admin Navigation",
                [
                    "📊 Dashboard & Analytics",
                    "📅 Event Management",
                    "👥 Participant Roster",
                    "🔍 Gate QR Scanner",
                ],
                label_visibility="collapsed",
            )
        else:
            page = st.radio(
                "Student Navigation",
                [
                    "🎪 Explore Events",
                    "🎟️ My Passes & QR Tickets",
                    "📊 My Student Dashboard",
                ],
                label_visibility="collapsed",
            )
            
        st.markdown("---")
        if st.button("🚪 Sign Out", use_container_width=True):
            logout_action()
    else:
        page = "Login"
        st.info("👋 Welcome! Sign in or use the 1-Click Demo buttons below to explore.")

    st.markdown("---")
    st.markdown("#### ⚙️ Demo Controls")
    st.caption("Reset sample database back to pristine initial state (8 events, fresh tickets).")
    if st.button("🔄 Reset Demo Database", use_container_width=True):
        with st.spinner("Resetting demo database..."):
            reset_database_action()
        st.success("Database restored to default demo state!")
        st.rerun()

    st.markdown("---")
    st.caption("Public Educational Demonstration • ₹0 Free Hosting • Streamlit Cloud")


# -------------------------------------------------------------
# AUTHENTICATION PAGE (When not signed in)
# -------------------------------------------------------------
if not st.session_state.authenticated:
    # Hero Banner
    st.markdown("""
    <div class="hero-banner">
        <div class="sandbox-badge">🎓 Public Educational Showcase • ₹0 Free Community Cloud Demo</div>
        <h1 class="hero-title">CampusConnect</h1>
        <p class="hero-subtitle">
            Smart College Event Registration & Gate Attendance System.<br>
            Featuring <b>sub-second QR pass verification</b>, <b>automated waitlist promotion</b>, and <b>real-time capacity analytics</b>.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 1-Click Instant Demo Login Buttons
    st.markdown("### ⚡ Instant Demo Access (1-Click)")
    demo_col1, demo_col2 = st.columns(2)
    
    with demo_col1:
        if st.button("🎓 Sign In as Demo Student (Alex Johnson)", use_container_width=True, type="primary"):
            async def _auth_student():
                async with async_session_maker() as db:
                    res = await db.execute(select(User).where(User.email == "student@campusconnect.com"))
                    return res.scalar_one_or_none()
            st_user = run_async(_auth_student())
            if st_user:
                login_action({
                    "id": st_user.id,
                    "email": st_user.email,
                    "full_name": st_user.full_name,
                    "is_admin": st_user.is_admin,
                    "department": st_user.department,
                })
                st.rerun()

    with demo_col2:
        if st.button("🛡️ Sign In as Demo Administrator (Admin)", use_container_width=True):
            async def _auth_admin():
                async with async_session_maker() as db:
                    res = await db.execute(select(User).where(User.email == "admin@campusconnect.com"))
                    return res.scalar_one_or_none()
            ad_user = run_async(_auth_admin())
            if ad_user:
                login_action({
                    "id": ad_user.id,
                    "email": ad_user.email,
                    "full_name": ad_user.full_name,
                    "is_admin": ad_user.is_admin,
                    "department": ad_user.department,
                })
                st.rerun()

    st.markdown("---")

    # Tabs for Manual Login / Register
    tab_signin, tab_signup = st.tabs(["🔐 Sign In with Password", "📝 New Student Registration"])
    
    with tab_signin:
        with st.form("signin_form"):
            email_in = st.text_input("College Email Address", placeholder="e.g. student@campusconnect.com")
            password_in = st.text_input("Password", type="password")
            submit_login = st.form_submit_button("Sign In", use_container_width=True)
            
            if submit_login:
                if not email_in or not password_in:
                    st.error("Please provide both email and password.")
                else:
                    async def _verify():
                        async with async_session_maker() as db:
                            res = await db.execute(select(User).where(User.email == email_in.strip()))
                            u = res.scalar_one_or_none()
                            if u and verify_password(password_in, u.hashed_password):
                                return {
                                    "id": u.id,
                                    "email": u.email,
                                    "full_name": u.full_name,
                                    "is_admin": u.is_admin,
                                    "department": u.department,
                                }
                            return None
                    user_match = run_async(_verify())
                    if user_match:
                        login_action(user_match)
                        st.rerun()
                    else:
                        st.error("Invalid email or password. You can also use the 1-Click Demo buttons above.")

    with tab_signup:
        with st.form("signup_form"):
            reg_name = st.text_input("Full Name", placeholder="e.g. Maya Patel")
            reg_email = st.text_input("College Email", placeholder="e.g. maya.patel@campusconnect.com")
            reg_dept = st.text_input("Academic Department", placeholder="e.g. Information Technology")
            reg_pass = st.text_input("Choose Password", type="password")
            submit_reg = st.form_submit_button("Create Student Account", use_container_width=True)

            if submit_reg:
                if not reg_name or not reg_email or not reg_pass:
                    st.error("Please complete all required fields.")
                else:
                    async def _register():
                        async with async_session_maker() as db:
                            # Check email exists
                            existing = await db.execute(select(User).where(User.email == reg_email.strip()))
                            if existing.scalar_one_or_none():
                                return False, "This email is already registered."
                            new_u = User(
                                email=reg_email.strip(),
                                full_name=reg_name.strip(),
                                hashed_password=get_password_hash(reg_pass),
                                department=reg_dept.strip() if reg_dept else "General",
                                is_admin=False,
                                is_active=True,
                            )
                            db.add(new_u)
                            await db.commit()
                            await db.refresh(new_u)
                            return True, {
                                "id": new_u.id,
                                "email": new_u.email,
                                "full_name": new_u.full_name,
                                "is_admin": new_u.is_admin,
                                "department": new_u.department,
                            }
                    ok, res = run_async(_register())
                    if ok:
                        st.success("Account created successfully! Logging you in...")
                        login_action(res)
                        st.rerun()
                    else:
                        st.error(res)

    # Public Event Preview for Guests
    st.markdown("---")
    st.markdown("### 📅 Upcoming Campus Events Preview")
    async def _get_public_events():
        async with async_session_maker() as db:
            events, _ = await event_service.get_events(db, page_size=6)
            return events
    preview_events = run_async(_get_public_events())
    
    cols = st.columns(3)
    for idx, ev in enumerate(preview_events):
        with cols[idx % 3]:
            seats_left = max(0, ev.capacity - ev.registered_count)
            status_text = f"🟢 {seats_left} seats remaining" if seats_left > 0 else "🟠 Waitlist Available"
            st.markdown(f"""
            <div class="event-card">
                <span style="background: #EEF2FF; color: #4338CA; padding: 0.2rem 0.6rem; border-radius: 4px; font-size: 0.75rem; font-weight: 700;">{ev.category}</span>
                <h4 style="margin: 0.6rem 0 0.3rem 0; color: #1E1B4B;">{ev.title}</h4>
                <p style="font-size: 0.85rem; color: #64748B; margin-bottom: 0.5rem;">
                    📅 {ev.date} • ⏰ {ev.time}<br>
                    📍 {ev.location}
                </p>
                <div style="font-size: 0.85rem; font-weight: 600;">{status_text}</div>
            </div>
            """, unsafe_allow_html=True)


# =============================================================
# STUDENT PORTAL (When signed in as student)
# =============================================================
elif st.session_state.authenticated and st.session_state.role == "student":
    user = st.session_state.user

    # ---------------------------------------------------------
    # TAB 1: EXPLORE EVENTS
    # ---------------------------------------------------------
    if page == "🎪 Explore Events":
        st.markdown(f"## 🎪 Discover Campus Events")
        st.caption(f"Browse, search, and reserve your seat with instant QR tickets.")

        search_col, cat_col = st.columns([3, 1])
        with search_col:
            search_query = st.text_input("🔍 Search events by title, keyword, or venue", placeholder="e.g. AI, Music, Hackathon...")
        with cat_col:
            category_filter = st.selectbox(
                "Filter Category",
                ["All", "technology", "cultural", "sports", "workshop", "seminar"],
            )

        # Query events from database
        async def _query_student_events():
            async with async_session_maker() as db:
                cat_arg = category_filter if category_filter != "All" else None
                search_arg = search_query.strip() if search_query else None
                events, total = await event_service.get_events(
                    db,
                    search=search_arg,
                    category=cat_arg,
                    page_size=50,
                )
                
                # Fetch user's active registrations to display status on card
                my_regs = await registration_service.get_user_registrations(db, user_id=user["id"])
                reg_map = {r["event_id"]: r for r in my_regs if r["status"] != "cancelled"}
                return events, reg_map

        events_list, user_reg_map = run_async(_query_student_events())

        if not events_list:
            st.info("No events match your search or filter. Try a different keyword!")
        else:
            for ev in events_list:
                seats_left = max(0, ev.capacity - ev.registered_count)
                is_full = ev.registered_count >= ev.capacity
                user_reg = user_reg_map.get(ev.id)

                with st.container():
                    st.markdown(f"""
                    <div class="event-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="background: #EEF2FF; color: #4338CA; padding: 0.2rem 0.6rem; border-radius: 4px; font-size: 0.8rem; font-weight: 700; text-transform: uppercase;">{ev.category}</span>
                            <span style="font-size: 0.85rem; font-weight: 700; color: {'#DC2626' if is_full else '#059669'};">
                                {'🟠 Capacity Full (Waitlist Open)' if is_full else f'🟢 {seats_left} / {ev.capacity} Seats Available'}
                            </span>
                        </div>
                        <h3 style="margin: 0.6rem 0 0.35rem 0; color: #1E1B4B;">{ev.title}</h3>
                        <p style="font-size: 0.9rem; color: #475569; margin-bottom: 0.6rem;">{ev.description or 'No description provided.'}</p>
                        <div style="display: flex; gap: 1.5rem; font-size: 0.85rem; color: #64748B;">
                            <div>📅 <b>{ev.date}</b></div>
                            <div>⏰ <b>{ev.time} {f'- {ev.end_time}' if ev.end_time else ''}</b></div>
                            <div>📍 <b>{ev.location}</b></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    btn_col1, btn_col2 = st.columns([1, 4])
                    with btn_col1:
                        if user_reg:
                            st_badge = user_reg["status"]
                            if st_badge == "confirmed":
                                st.success("✅ Registered (Confirmed)")
                            elif st_badge == "waitlisted":
                                st.warning(f"⏳ Waitlist Position #{user_reg.get('waitlist_position', 1)}")
                            elif st_badge == "attended":
                                st.info("🎉 Attended")
                        else:
                            btn_label = "⏳ Join Waitlist" if is_full else "🎟️ Register for Event"
                            if st.button(btn_label, key=f"reg_btn_{ev.id}", type="primary" if not is_full else "secondary"):
                                async def _do_register():
                                    async with async_session_maker() as db:
                                        try:
                                            reg = await registration_service.register_for_event(
                                                db, user_id=user["id"], event_id=ev.id
                                            )
                                            return True, reg.status, reg.waitlist_position
                                        except ValueError as e:
                                            return False, str(e), None
                                ok, status_res, pos = run_async(_do_register())
                                if ok:
                                    if status_res == "confirmed":
                                        st.balloons()
                                        st.success("🎉 Registration Confirmed! Your digital pass is ready under 'My Passes'.")
                                    else:
                                        st.warning(f"⏳ Event at capacity. You are placed on the Priority Waitlist at position #{pos}!")
                                    st.rerun()
                                else:
                                    st.error(f"Registration error: {status_res}")
                    st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # TAB 2: MY TICKETS & PASSES
    # ---------------------------------------------------------
    elif page == "🎟️ My Passes & QR Tickets":
        st.markdown(f"## 🎟️ My Registered Passes & Tickets")
        st.caption("Present your QR ticket at the gate for rapid check-in entry.")

        async def _get_my_passes():
            async with async_session_maker() as db:
                return await registration_service.get_user_registrations(db, user_id=user["id"])

        my_passes = run_async(_get_my_passes())

        if not my_passes:
            st.info("You haven't registered for any events yet. Explore events to grab a pass!")
        else:
            for reg in my_passes:
                status_color = {
                    "confirmed": "badge-confirmed",
                    "waitlisted": "badge-waitlisted",
                    "attended": "badge-attended",
                    "cancelled": "badge-cancelled",
                }.get(reg["status"], "badge-confirmed")

                with st.container():
                    st.markdown(f"""
                    <div class="ticket-container">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                            <div>
                                <span class="{status_color}">{reg['status'].upper()}{f' (Position #{reg["waitlist_position"]})' if reg.get('waitlist_position') else ''}</span>
                                <h3 style="margin: 0.5rem 0 0.2rem 0; color: #1E1B4B;">{reg['event_title']}</h3>
                                <p style="font-size: 0.85rem; color: #64748B; margin-bottom: 0.5rem;">
                                    📅 {reg['event_date']} • ⏰ {reg['event_time']} • 📍 {reg['event_location']}
                                </p>
                                <p style="font-size: 0.85rem; color: #334155; margin: 0;">
                                    <b>Attendee:</b> {user['full_name']} ({user['email']})<br>
                                    <b>Pass ID:</b> <code>{reg['qr_code']}</code>
                                </p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    ticket_col1, ticket_col2 = st.columns([1, 2])
                    with ticket_col1:
                        if reg["status"] in ["confirmed", "attended"]:
                            qr_img = make_qr_image(reg["qr_code"])
                            st.image(qr_img, width=175, caption=f"Gate Pass QR ({reg['qr_code'][:12]}...)")
                            
                            # Download QR button
                            buf = io.BytesIO()
                            qr_img.save(buf, format="PNG")
                            st.download_button(
                                label="📥 Download Pass",
                                data=buf.getvalue(),
                                file_name=f"ticket_{reg['event_id']}_{reg['id']}.png",
                                mime="image/png",
                                key=f"dl_qr_{reg['id']}",
                            )
                        elif reg["status"] == "waitlisted":
                            st.info(f"⏳ **Waitlist Position #{reg.get('waitlist_position', 1)}**\n\nIf a confirmed attendee cancels, you will automatically be promoted and your QR pass will activate immediately.")
                        elif reg["status"] == "cancelled":
                            st.caption("Pass was cancelled.")

                    with ticket_col2:
                        if reg["status"] in ["confirmed", "waitlisted"]:
                            st.markdown("#### Pass Actions")
                            st.caption("If you can no longer attend, please cancel so a waitlisted classmate can take your seat.")
                            if st.button("❌ Cancel Registration", key=f"cancel_{reg['event_id']}", type="secondary"):
                                async def _cancel():
                                    async with async_session_maker() as db:
                                        return await registration_service.cancel_registration(
                                            db, user_id=user["id"], event_id=reg["event_id"]
                                        )
                                cancelled_reg = run_async(_cancel())
                                if cancelled_reg:
                                    st.success("Registration cancelled. Any waitlisted student has been automatically promoted!")
                                    st.rerun()

                    st.markdown("<hr style='margin: 1.5rem 0;'>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # TAB 3: STUDENT DASHBOARD
    # ---------------------------------------------------------
    elif page == "📊 My Student Dashboard":
        st.markdown(f"## 📊 Student Dashboard — {user['full_name']}")
        st.caption(f"Student ID: STU-{user['id']:04d} • {user['department']}")

        async def _get_student_stats():
            async with async_session_maker() as db:
                my_regs = await registration_service.get_user_registrations(db, user_id=user["id"])
                return my_regs
        regs = run_async(_get_student_stats())

        confirmed_count = sum(1 for r in regs if r["status"] == "confirmed")
        waitlist_count = sum(1 for r in regs if r["status"] == "waitlisted")
        attended_count = sum(1 for r in regs if r["status"] == "attended")

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{confirmed_count}</div>
                <div class="metric-label">Active Confirmed Passes</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{waitlist_count}</div>
                <div class="metric-label">Waitlisted Queues</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{attended_count}</div>
                <div class="metric-label">Events Attended</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 📋 Registration Activity History")
        if regs:
            table_data = []
            for r in regs:
                table_data.append({
                    "Event Title": r["event_title"],
                    "Date": r["event_date"],
                    "Time": r["event_time"],
                    "Status": r["status"].upper(),
                    "Waitlist Position": r.get("waitlist_position") or "-",
                    "Ticket ID": r["qr_code"][:16] + "...",
                })
            st.dataframe(pd.DataFrame(table_data), use_container_width=True)
        else:
            st.info("No registration activity recorded.")


# =============================================================
# ADMINISTRATOR PORTAL (When signed in as admin)
# =============================================================
elif st.session_state.authenticated and st.session_state.role == "admin":
    admin_user = st.session_state.user

    # ---------------------------------------------------------
    # TAB 1: DASHBOARD & ANALYTICS
    # ---------------------------------------------------------
    if page == "📊 Dashboard & Analytics":
        st.markdown("## 📊 Executive Event & Gate Analytics")
        st.caption("Live attendance telemetry, registration velocity, and genre distributions.")

        async def _fetch_admin_analytics():
            async with async_session_maker() as db:
                analytics = await analytics_service.get_dashboard_analytics(db)
                cat_stats = await analytics_service.get_event_category_stats(db)
                events, _ = await event_service.get_events(db, page_size=100)
                return analytics, cat_stats, events

        analytics_data, cat_stats_data, all_events = run_async(_fetch_admin_analytics())

        # Top KPI Metrics
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{analytics_data['total_events']}</div>
                <div class="metric-label">Total Events</div>
            </div>
            """, unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{analytics_data['total_registrations']}</div>
                <div class="metric-label">Total Registrations</div>
            </div>
            """, unsafe_allow_html=True)
        with m3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{analytics_data['attendance_rate_percent']}%</div>
                <div class="metric-label">Gate Turnout Rate</div>
            </div>
            """, unsafe_allow_html=True)
        with m4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{analytics_data['waitlisted_registrations']}</div>
                <div class="metric-label">Waitlisted Students</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Visual Plotly Charts
        ch_col1, ch_col2 = st.columns(2)
        with ch_col1:
            st.markdown("#### Event Registration Status Breakdown")
            chart_status_df = pd.DataFrame([
                {"Status": "Confirmed", "Count": analytics_data["confirmed_registrations"]},
                {"Status": "Attended", "Count": analytics_data["attended_registrations"]},
                {"Status": "Waitlisted", "Count": analytics_data["waitlisted_registrations"]},
            ])
            fig_bar = px.bar(
                chart_status_df,
                x="Status",
                y="Count",
                color="Status",
                color_discrete_map={"Confirmed": "#10B981", "Attended": "#6366F1", "Waitlisted": "#F59E0B"},
                text="Count",
            )
            fig_bar.update_layout(showlegend=False, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_bar, use_container_width=True)

        with ch_col2:
            st.markdown("#### Events by Category Distribution")
            if cat_stats_data:
                cat_df = pd.DataFrame(cat_stats_data)
                fig_pie = px.pie(
                    cat_df,
                    names="category",
                    values="event_count",
                    hole=0.45,
                    color_discrete_sequence=px.colors.qualitative.Prism,
                )
                fig_pie.update_layout(margin=dict(l=20, r=20, t=20, b=20))
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("No category data available.")

    # ---------------------------------------------------------
    # TAB 2: EVENT MANAGEMENT
    # ---------------------------------------------------------
    elif page == "📅 Event Management":
        st.markdown("## 📅 Event Lifecycle & Capacity Hub")
        st.caption("Create new events, tune maximum seat capacities, and update event schedules.")

        sub_tab_create, sub_tab_manage = st.tabs(["➕ Create New Event", "✏️ Edit / Delete Existing Events"])

        with sub_tab_create:
            with st.form("create_event_form"):
                c1, c2 = st.columns(2)
                with c1:
                    ev_title = st.text_input("Event Title *", placeholder="e.g. AI Innovation Summit 2026")
                    ev_cat = st.selectbox("Category *", ["technology", "cultural", "sports", "workshop", "seminar"])
                    ev_loc = st.text_input("Location / Venue *", placeholder="e.g. Main Auditorium")
                    ev_cap = st.number_input("Maximum Capacity (Seats) *", min_value=1, max_value=5000, value=50)
                with c2:
                    ev_date = st.date_input("Event Date *", min_value=datetime.now().date())
                    ev_time = st.text_input("Start Time *", value="10:00 AM", placeholder="e.g. 10:00 AM")
                    ev_end_time = st.text_input("End Time", value="01:00 PM", placeholder="e.g. 01:00 PM")
                    ev_img = st.text_input("Banner Image URL (Optional)", value="https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800")
                
                ev_desc = st.text_area("Event Description", placeholder="Details about this campus event...")
                submit_create = st.form_submit_button("🚀 Publish Event", use_container_width=True, type="primary")

                if submit_create:
                    if not ev_title or not ev_loc:
                        st.error("Please fill in all mandatory fields.")
                    else:
                        async def _publish():
                            async with async_session_maker() as db:
                                return await event_service.create_event(
                                    db,
                                    title=ev_title.strip(),
                                    description=ev_desc.strip(),
                                    date=str(ev_date),
                                    time=ev_time.strip(),
                                    end_time=ev_end_time.strip() if ev_end_time else None,
                                    location=ev_loc.strip(),
                                    category=ev_cat,
                                    capacity=ev_cap,
                                    image_url=ev_img.strip() if ev_img else None,
                                    created_by=admin_user["id"],
                                )
                        new_ev = run_async(_publish())
                        st.success(f"🎉 Event '{new_ev.title}' created successfully with capacity {new_ev.capacity}!")
                        st.rerun()

        with sub_tab_manage:
            async def _load_all_events():
                async with async_session_maker() as db:
                    evs, _ = await event_service.get_events(db, page_size=100)
                    return evs
            current_events = run_async(_load_all_events())

            if not current_events:
                st.info("No events registered.")
            else:
                selected_event_title = st.selectbox(
                    "Select Event to Inspect or Modify",
                    options=[f"#{e.id}: {e.title} ({e.date})" for e in current_events],
                )
                sel_id = int(selected_event_title.split(":")[0].replace("#", ""))
                selected_event = next(e for e in current_events if e.id == sel_id)

                st.markdown(f"### Editing: **{selected_event.title}**")
                with st.form("edit_event_form"):
                    e_col1, e_col2 = st.columns(2)
                    with e_col1:
                        up_title = st.text_input("Title", value=selected_event.title)
                        up_cat = st.selectbox("Category", ["technology", "cultural", "sports", "workshop", "seminar"], index=["technology", "cultural", "sports", "workshop", "seminar"].index(selected_event.category) if selected_event.category in ["technology", "cultural", "sports", "workshop", "seminar"] else 0)
                        up_loc = st.text_input("Venue", value=selected_event.location)
                    with e_col2:
                        up_cap = st.number_input("Capacity", min_value=1, max_value=5000, value=selected_event.capacity)
                        up_time = st.text_input("Time", value=selected_event.time)
                        up_date = st.text_input("Date (YYYY-MM-DD)", value=selected_event.date)
                    
                    up_desc = st.text_area("Description", value=selected_event.description or "")
                    
                    save_btn = st.form_submit_button("💾 Save Changes", type="primary")
                    if save_btn:
                        async def _update():
                            async with async_session_maker() as db:
                                return await event_service.update_event(
                                    db,
                                    event_id=selected_event.id,
                                    title=up_title.strip(),
                                    category=up_cat,
                                    location=up_loc.strip(),
                                    capacity=up_cap,
                                    time=up_time.strip(),
                                    date=up_date.strip(),
                                    description=up_desc.strip(),
                                )
                        updated_ev = run_async(_update())
                        st.success(f"Event updated successfully! Max capacity: {updated_ev.capacity}")
                        st.rerun()

                st.markdown("#### Danger Zone")
                if st.button("🗑️ Delete This Event", key=f"del_ev_{selected_event.id}", type="secondary"):
                    async def _del():
                        async with async_session_maker() as db:
                            return await event_service.delete_event(db, selected_event.id)
                    run_async(_del())
                    st.warning(f"Event #{selected_event.id} deleted.")
                    st.rerun()

    # ---------------------------------------------------------
    # TAB 3: PARTICIPANT ROSTER & CSV EXPORTS
    # ---------------------------------------------------------
    elif page == "👥 Participant Roster":
        st.markdown("## 👥 Attendee Rosters & CSV Export")
        st.caption("Inspect participant registrations, verify ticket statuses, and export RFC 4180 audit sheets.")

        async def _load_events_for_roster():
            async with async_session_maker() as db:
                evs, _ = await event_service.get_events(db, page_size=100)
                return evs
        roster_events = run_async(_load_events_for_roster())

        if not roster_events:
            st.info("No events found.")
        else:
            roster_sel = st.selectbox(
                "Select Event Roster",
                options=[f"#{e.id}: {e.title} ({e.date})" for e in roster_events],
            )
            roster_event_id = int(roster_sel.split(":")[0].replace("#", ""))

            async def _get_participants():
                async with async_session_maker() as db:
                    return await registration_service.get_event_participants(db, roster_event_id)
            participants = run_async(_get_participants())

            # Export Buttons
            exp_col1, exp_col2 = st.columns([1, 1])
            with exp_col1:
                csv_all = export_registrations_csv(participants)
                st.download_button(
                    label="📥 Download Full Registrations CSV",
                    data=csv_all,
                    file_name=f"event_{roster_event_id}_registrations.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
            with exp_col2:
                attendees_only = [p for p in participants if p["status"] == "attended"]
                csv_attendees = export_attendees_csv(attendees_only)
                st.download_button(
                    label="📥 Download Verified Attendees CSV",
                    data=csv_attendees,
                    file_name=f"event_{roster_event_id}_attendees.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

            st.markdown("---")

            # Filters & Search
            f_col1, f_col2 = st.columns([2, 1])
            with f_col1:
                search_student = st.text_input("🔍 Search by student name or email", placeholder="Type name or email...")
            with f_col2:
                status_filter = st.selectbox("Status Filter", ["All", "confirmed", "attended", "waitlisted", "cancelled"])

            # Filter data
            filtered_p = participants
            if search_student:
                q = search_student.lower().strip()
                filtered_p = [p for p in filtered_p if q in p.get("user_name", "").lower() or q in p.get("user_email", "").lower()]
            if status_filter != "All":
                filtered_p = [p for p in filtered_p if p.get("status") == status_filter]

            st.markdown(f"Showing **{len(filtered_p)}** of **{len(participants)}** participants")

            if filtered_p:
                p_table = []
                for p in filtered_p:
                    p_table.append({
                        "Student Name": p.get("user_name"),
                        "Email": p.get("user_email"),
                        "Department": p.get("user_department"),
                        "Status": p.get("status", "").upper(),
                        "Waitlist #": p.get("waitlist_position") or "-",
                        "Pass Code": p.get("qr_code")[:16] + "...",
                        "Registered At": p.get("registered_at"),
                    })
                st.dataframe(pd.DataFrame(p_table), use_container_width=True)
            else:
                st.info("No participants matching the selected filter.")

    # ---------------------------------------------------------
    # TAB 4: GATE QR SCANNER & ATTENDANCE VERIFICATION
    # ---------------------------------------------------------
    elif page == "🔍 Gate QR Scanner":
        st.markdown("## 🔍 Gate QR Attendance Scanner")
        st.caption("Sub-second pass verification with instant duplicate check-in prevention.")

        scan_tab_cam, scan_tab_upload, scan_tab_manual = st.tabs([
            "📷 Camera Live Scanner",
            "📁 Upload Ticket Image",
            "⌨️ Manual Ticket Code Entry",
        ])

        target_code = None

        with scan_tab_cam:
            st.markdown("##### Scan Student Pass using Device Camera")
            cam_image = st.camera_input("Point camera at attendee's QR ticket")
            if cam_image is not None:
                decoded = decode_qr_image(cam_image.getvalue())
                if decoded:
                    target_code = decoded
                    st.success(f"Detected QR Code: `{target_code}`")
                else:
                    st.warning("No clear QR code detected in the camera frame. Ensure good lighting or try image upload.")

        with scan_tab_upload:
            st.markdown("##### Upload QR Ticket Image File")
            uploaded_file = st.file_uploader("Upload PNG or JPEG pass", type=["png", "jpg", "jpeg"])
            if uploaded_file is not None:
                decoded = decode_qr_image(uploaded_file.getvalue())
                if decoded:
                    target_code = decoded
                    st.success(f"Decoded QR Code: `{target_code}`")
                else:
                    st.error("Could not decode a valid QR code from this image file.")

        with scan_tab_manual:
            st.markdown("##### Keyboard / Barcode Reader Input")
            manual_code = st.text_input("Enter or paste Ticket QR payload", placeholder="e.g. 98343adc-f4f2-4641-...")
            if st.button("Verify Manual Code", key="btn_manual_verify"):
                if manual_code.strip():
                    target_code = manual_code.strip()

        # If a target code was scanned/entered, execute gate check-in
        if target_code:
            st.markdown("---")
            st.markdown("### Verification Result")
            async def _verify_and_mark():
                async with async_session_maker() as db:
                    try:
                        res = await attendance_service.mark_attended(db, qr_code=target_code)
                        return True, res
                    except ValueError as e:
                        return False, str(e)

            ok, result_data = run_async(_verify_and_mark())

            if ok:
                st.balloons()
                st.markdown(f"""
                <div style="background: #DEF7EC; border: 2px solid #059669; border-radius: 0.85rem; padding: 1.25rem; margin-bottom: 1rem;">
                    <div style="font-size: 1.25rem; font-weight: 800; color: #065F46;">
                        ✅ Entry Granted — Check-in Successful!
                    </div>
                    <p style="margin: 0.5rem 0 0 0; color: #047857; font-size: 0.95rem;">
                        <b>Attendee:</b> {result_data['student']['name']} ({result_data['student']['email']})<br>
                        <b>Event:</b> {result_data['event']['title']}<br>
                        <b>Schedule:</b> {result_data['event']['date']} • {result_data['event']['time']}<br>
                        <b>Status:</b> Marked as <b>ATTENDED</b>
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Append to recent scans audit log
                st.session_state.recent_scans.insert(0, {
                    "Attendee": result_data['student']['name'],
                    "Event": result_data['event']['title'],
                    "Time": datetime.now(timezone.utc).strftime("%H:%M:%S UTC"),
                    "Result": "✅ Verified & Attended",
                    "Ticket ID": target_code[:16] + "...",
                })
            else:
                err_msg = str(result_data)
                is_duplicate = "already marked" in err_msg.lower()
                st.markdown(f"""
                <div style="background: {'#FEF3C7' if is_duplicate else '#FEE2E2'}; border: 2px solid {'#D97706' if is_duplicate else '#DC2626'}; border-radius: 0.85rem; padding: 1.25rem; margin-bottom: 1rem;">
                    <div style="font-size: 1.25rem; font-weight: 800; color: {'#92400E' if is_duplicate else '#991B1B'};">
                        {'⚠️ Duplicate Check-in Rejected!' if is_duplicate else '❌ Entry Denied'}
                    </div>
                    <p style="margin: 0.5rem 0 0 0; color: {'#78350F' if is_duplicate else '#7F1D1D'}; font-size: 0.95rem;">
                        {err_msg}
                    </p>
                </div>
                """, unsafe_allow_html=True)

                st.session_state.recent_scans.insert(0, {
                    "Attendee": "Unknown / N/A",
                    "Event": "N/A",
                    "Time": datetime.now(timezone.utc).strftime("%H:%M:%S UTC"),
                    "Result": f"❌ Rejected ({err_msg})",
                    "Ticket ID": target_code[:16] + "...",
                })

        # Recent Scans Audit Table
        st.markdown("---")
        st.markdown("### 📋 Recent Gate Scans Audit Log")
        if st.session_state.recent_scans:
            st.dataframe(pd.DataFrame(st.session_state.recent_scans[:15]), use_container_width=True)
        else:
            st.caption("No scans recorded in this gate session yet.")
