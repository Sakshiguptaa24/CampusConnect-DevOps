import pytest

@pytest.mark.asyncio
async def test_register_success(client):
    response = await client.post(
        "/api/auth/register",
        json={
            "email": "newuser@campusconnect.com",
            "password": "Password123!",
            "full_name": "New User",
            "department": "Physics",
            "phone": "+1 555-9999",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@campusconnect.com"
    assert data["full_name"] == "New User"
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    response = await client.post(
        "/api/auth/register",
        json={
            "email": "test_student@campusconnect.com",
            "password": "Password123!",
            "full_name": "Duplicate Student",
        },
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_success(client):
    response = await client.post(
        "/api/auth/login",
        json={
            "email": "test_student@campusconnect.com",
            "password": "StudentPass123!",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "test_student@campusconnect.com"


@pytest.mark.asyncio
async def test_login_invalid_password(client):
    response = await client.post(
        "/api/auth/login",
        json={
            "email": "test_student@campusconnect.com",
            "password": "WrongPassword123!",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_profile(client, student_headers):
    response = await client.get("/api/auth/me", headers=student_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test_student@campusconnect.com"
