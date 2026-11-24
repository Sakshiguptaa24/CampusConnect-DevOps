import pytest

@pytest.mark.asyncio
async def test_registration_flow_and_waitlist_promotion(client, admin_headers, student_headers):
    # 1. Admin creates a tiny capacity event (capacity = 1)
    ev_resp = await client.post(
        "/api/events",
        json={
            "title": "VIP Masterclass (Capacity 1)",
            "description": "Exclusive single-seat workshop.",
            "date": "2026-12-20",
            "time": "15:00",
            "end_time": "16:00",
            "location": "VIP Boardroom",
            "category": "Workshop",
            "capacity": 1,
        },
        headers=admin_headers,
    )
    assert ev_resp.status_code == 201
    event_id = ev_resp.json()["id"]

    # 2. Student registers -> Should be "confirmed"
    reg1 = await client.post(
        "/api/registrations",
        json={"event_id": event_id},
        headers=student_headers,
    )
    assert reg1.status_code == 201
    reg1_data = reg1.json()
    assert reg1_data["status"] == "confirmed"
    assert reg1_data["waitlist_position"] is None
    assert "qr_code" in reg1_data

    # 3. Duplicate registration attempt -> Should fail with 400
    dup_reg = await client.post(
        "/api/registrations",
        json={"event_id": event_id},
        headers=student_headers,
    )
    assert dup_reg.status_code == 400
    assert "already registered" in dup_reg.json()["detail"].lower()

    # 4. Create a second student and register for the full event -> Should be "waitlisted"
    reg2_user = await client.post(
        "/api/auth/register",
        json={
            "email": "student2_test@campusconnect.com",
            "password": "Password123!",
            "full_name": "Second Student",
        },
    )
    assert reg2_user.status_code == 201
    login_resp = await client.post(
        "/api/auth/login",
        json={
            "email": "student2_test@campusconnect.com",
            "password": "Password123!",
        },
    )
    token2 = login_resp.json()["access_token"]
    student2_headers = {"Authorization": f"Bearer {token2}"}

    reg2 = await client.post(
        "/api/registrations",
        json={"event_id": event_id},
        headers=student2_headers,
    )
    assert reg2.status_code == 201
    reg2_data = reg2.json()
    assert reg2_data["status"] == "waitlisted"
    assert reg2_data["waitlist_position"] == 1

    # 5. First student cancels registration
    cancel_resp = await client.delete(
        f"/api/registrations/{event_id}",
        headers=student_headers,
    )
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["status"] == "cancelled"

    # 6. Verify second student is automatically promoted to "confirmed"!
    reg2_my = await client.get("/api/registrations/my", headers=student2_headers)
    assert reg2_my.status_code == 200
    my_regs = reg2_my.json()
    promoted = next((r for r in my_regs if r["event_id"] == event_id), None)
    assert promoted is not None
    assert promoted["status"] == "confirmed"
    assert promoted["waitlist_position"] is None
