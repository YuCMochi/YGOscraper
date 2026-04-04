"""
tests/api/test_health.py - API contract test for /health endpoint

Uses httpx.AsyncClient with ASGITransport.
Mocks card_db.initialize() to avoid downloading real files on startup.
"""
from unittest.mock import patch

import httpx
import pytest

from server import app


@pytest.fixture
async def client():
    """Async test client with mocked lifespan."""
    with patch("server.card_db.initialize"), patch("server.card_db.close"):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as c:
            yield c


class TestHealthEndpoint:
    async def test_health_dependencies_returns_200(self, client):
        """5.1 GET /api/health/dependencies 回傳 200"""
        with patch("app.routers.health._check_one") as mock_check:
            from app.routers.health import DependencyStatus
            mock_check.return_value = DependencyStatus(
                name="test", url="http://test", ok=True, status_code=200
            )
            response = await client.get("/api/health/dependencies")

        assert response.status_code == 200

    async def test_health_response_schema(self, client):
        """5.1 回應包含 all_ok 和 results 欄位"""
        with patch("app.routers.health._check_one") as mock_check:
            from app.routers.health import DependencyStatus
            mock_check.return_value = DependencyStatus(
                name="test", url="http://test", ok=True, status_code=200
            )
            response = await client.get("/api/health/dependencies")

        data = response.json()
        assert "all_ok" in data
        assert "results" in data
        assert isinstance(data["results"], list)
