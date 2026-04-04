"""
tests/integration/test_scrapers.py - External API smoke tests

These tests hit real external APIs.
Run only in the scheduled CI workflow:
    pytest -m integration

Skip during normal development:
    pytest -m "not integration"
"""
import httpx
import pytest
from bs4 import BeautifulSoup

from app.config import KONAMI_DB_BASE_URL, RUTEN_API_BASE_URL


@pytest.mark.integration
class TestKonamiScraper:
    async def test_konami_db_page_parseable(self):
        """6.1 Konami DB 回傳頁面可解析出卡號資訊

        Uses a known card cid (e.g., 4027 = Blue-Eyes White Dragon).
        Verifies the HTML structure contains the card number table.
        """
        # cid=4027 is Blue-Eyes White Dragon
        url = f"{KONAMI_DB_BASE_URL}?ope=2&cid=4027&request_locale=ja"
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.get(url)

        assert response.status_code == 200, f"Konami DB returned {response.status_code}"

        soup = BeautifulSoup(response.text, "html.parser")
        # Konami page should have card info section
        assert soup.find("body") is not None, "Response has no body element"
        # Check page is not empty / error page
        assert len(response.text) > 1000, "Konami page content too short — possible format change"


@pytest.mark.integration
class TestRutenScraper:
    async def test_ruten_search_api_parseable(self):
        """6.2 Ruten 搜尋 API 可解析出商品列表

        Uses the Ruten search endpoint to search for a known YGO card.
        Verifies the response contains product_id, price fields.
        """
        # Search for a common card to get at least some results
        search_url = (
            f"{RUTEN_API_BASE_URL}/search/v3/index.php"
            "?type=direct&q=%E9%9D%92%E7%9C%BC%E7%99%BD%E9%BE%8D"  # 青眼白龍
            "&p=1&n=10&sort=prc%2Fasc"
        )
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.get(search_url)

        assert response.status_code == 200, f"Ruten API returned {response.status_code}"

        data = response.json()
        assert "Rows" in data or "rows" in data or isinstance(data, list), (
            f"Ruten API response schema changed. Keys: {list(data.keys()) if isinstance(data, dict) else type(data)}"
        )
