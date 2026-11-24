import pytest

@pytest.mark.asyncio
async def test_qr_attendance_and_duplicate_checkin_prevention(client, admin_headers, student_headers):
    # 1. Admin creates an event
    ev_resp = await client.post(
        "/api/events",
        json={
            "title": "Robotics Expo",
            "description": "Showcase of autonomous robotics.",
            "date": "2026-12-25",
            "time": "10:00",
            "location": "Robotics Lab",
            "category": "Technology",
            "capacity": 50,
        },
        headers=admin_headers,
    )
    event_id = ev_resp.json()["id"]

    # 2. Student registers
    reg_resp = await client.post(
        "/api/registrations",
        json={"event_id": event_id},
        headers=student_headers,
    )
    assert reg_resp.status_code == 201
    qr_code = reg_resp.json()["qr_code"]

    # 3. Lookup QR info
    lookup_resp = await client.get(f"/api/attendance/verify/{qr_code}", headers=student_headers)
    assert lookup_resp.status_code == 200
    info = lookup_resp.json()
    assert info["valid"] is True
    assert info["status"] == "confirmed"

    # 4. Admin verifies attendance via QR scan
    verify_resp = await client.post(
        "/api/attendance/verify",
        json={"qr_code": qr_code},
        headers=admin_headers,
    )
    assert verify_resp.status_code == 200
    assert verify_resp.json()["status"] == "attended"

    # 5. Duplicate check-in attempt -> should fail with error
    dup_verify = await client.post(
        "/api/attendance/verify",
        json={"qr_code": qr_code},
        headers=admin_headers,
    )
    assert dup_verify.status_code == 400
    assert "already marked" in dup_verify.json()["detail"].lower()

    # 6. Admin checks attendance stats
    stats_resp = await client.get(f"/api/attendance/stats/{event_id}", headers=admin_headers)
    assert stats_resp.status_code == 200
    stats = stats_resp.json()
    assert stats["attended_count"] == 1

    # 7. Admin exports registrations CSV
    csv_resp = await client.get(f"/api/admin/events/{event_id}/export-csv", headers=admin_headers)
    assert csv_resp.status_code == 200
    assert "text/csv" in csv_resp.headers["content-type"]
    assert "User Email" in csv_resp.text
