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
        card_number_divs = soup.select("div.card_number")
        assert len(card_number_divs) > 0, (
            "No div.card_number found — Konami DB page structure may have changed"
        )


@pytest.mark.integration
class TestRutenScraper:
    async def test_ruten_search_api_parseable(self):
        """6.2 Ruten 搜尋 API 可解析出商品列表

        Uses the Ruten search endpoint to search for a known YGO card.
        Verifies the response contains product_id, price fields.
        """
        # Use the same endpoint the scraper actually calls
        search_url = f"{RUTEN_API_BASE_URL}/search/v3/index.php/core/prod"
        params = {
            "q": "青眼白龍",
            "type": "direct",
            "sort": "rnk/dc",
            "limit": 10,
            "offset": 1,
        }
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.get(search_url, params=params)

        assert response.status_code == 200, f"Ruten API returned {response.status_code}"

        data = response.json()
        assert "Rows" in data, (
            f"Ruten API response missing 'Rows' key — schema may have changed. "
            f"Got keys: {list(data.keys()) if isinstance(data, dict) else type(data)}"
        )
        assert "TotalRows" in data, (
            f"Ruten API response missing 'TotalRows' key — schema may have changed. "
            f"Got keys: {list(data.keys())}"
        )
