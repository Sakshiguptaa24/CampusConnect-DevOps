import asyncio
import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.core.database import Base, get_db
from app.core.security import get_password_hash, create_access_token
from app.models.user import User
from app.models.event import Event
from app.models.registration import Registration
from app.main import app

TEST_DB_FILE = "./test_suite.db"
TEST_DATABASE_URL = f"sqlite+aiosqlite:///{TEST_DB_FILE}"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_test_db():
    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
        except OSError:
            pass

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed admin and student
    async with TestingSessionLocal() as session:
        admin = User(
            email="test_admin@campusconnect.com",
            full_name="Test Admin",
            hashed_password=get_password_hash("AdminPass123!"),
            is_admin=True,
            is_active=True,
            department="Admin Dept",
        )
        student = User(
            email="test_student@campusconnect.com",
            full_name="Test Student",
            hashed_password=get_password_hash("StudentPass123!"),
            is_admin=False,
            is_active=True,
            department="CS",
        )
        session.add_all([admin, student])
        await session.commit()

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
        except OSError:
            pass


async def override_get_db():
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def admin_token():
    async with TestingSessionLocal() as session:
        from sqlalchemy import select
        res = await session.execute(
            select(User).where(User.email == "test_admin@campusconnect.com")
        )
        user = res.scalar_one()
        return create_access_token({"sub": str(user.id), "email": user.email, "is_admin": True})


@pytest_asyncio.fixture
async def student_token():
    async with TestingSessionLocal() as session:
        from sqlalchemy import select
        res = await session.execute(
            select(User).where(User.email == "test_student@campusconnect.com")
        )
        user = res.scalar_one()
        return create_access_token({"sub": str(user.id), "email": user.email, "is_admin": False})


@pytest_asyncio.fixture
async def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest_asyncio.fixture
async def student_headers(student_token):
    return {"Authorization": f"Bearer {student_token}"}
