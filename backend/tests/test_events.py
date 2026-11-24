import pytest

@pytest.mark.asyncio
async def test_create_event_admin_only(client, admin_headers, student_headers):
    payload = {
        "title": "Quantum Computing Seminar",
        "description": "Introduction to qubits and quantum algorithms.",
        "date": "2026-12-15",
        "time": "14:00",
        "end_time": "16:00",
        "location": "Physics Hall 101",
        "category": "Technology",
        "capacity": 25,
    }

    # Student should be forbidden
    student_resp = await client.post("/api/events", json=payload, headers=student_headers)
    assert student_resp.status_code == 403

    # Admin should succeed
    admin_resp = await client.post("/api/events", json=payload, headers=admin_headers)
    assert admin_resp.status_code == 201
    created = admin_resp.json()
    assert created["title"] == payload["title"]
    assert created["capacity"] == 25
    assert created["registered_count"] == 0


@pytest.mark.asyncio
async def test_list_and_search_events(client):
    # Public list
    resp = await client.get("/api/events?page=1&page_size=10")
    assert resp.status_code == 200
    data = resp.json()
    assert "events" in data
    assert data["total"] >= 1

    # Search
    search_resp = await client.get("/api/events?search=Quantum")
    assert search_resp.status_code == 200
    search_data = search_resp.json()
    assert len(search_data["events"]) >= 1
    assert "Quantum" in search_data["events"][0]["title"]

    # Category filter
    cat_resp = await client.get("/api/events?category=Technology")
    assert cat_resp.status_code == 200
    cat_data = cat_resp.json()
    assert all(e["category"] == "Technology" for e in cat_data["events"])
