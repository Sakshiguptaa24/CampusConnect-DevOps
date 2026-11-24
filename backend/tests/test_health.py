import pytest

@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data


@pytest.mark.asyncio
async def test_readiness_check(client):
    response = await client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["checks"]["database"] == "ok"


@pytest.mark.asyncio
async def test_prometheus_metrics(client):
    response = await client.get("/metrics")
    assert response.status_code == 200
    assert "campusconnect_requests_total" in response.text
    assert "campusconnect_uptime_seconds" in response.text
