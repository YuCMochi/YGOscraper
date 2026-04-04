"""
tests/integration/test_external_resources.py - salix5 resource smoke tests

Verifies that salix5 GitHub resources are accessible and in expected format.
All tests are marked @pytest.mark.integration — run only in scheduled CI.
"""
import httpx
import pytest

from app.config import CARD_IMAGE_BASE_URL, CARDS_CDB_URL, CID_TABLE_URL

SQLITE_MAGIC = b"SQLite format 3"

# A known valid passcode for Blue-Eyes White Dragon
KNOWN_PASSCODE = "89631139"


@pytest.mark.integration
class TestCardsCdb:
    async def test_cards_cdb_downloadable_and_sqlite(self):
        """6.3 cards.cdb 可下載且為合法 SQLite 資料庫"""
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(CARDS_CDB_URL)

        assert response.status_code == 200, (
            f"cards.cdb download failed with status {response.status_code}"
        )
        # SQLite files start with "SQLite format 3\000"
        assert response.content[:15] == SQLITE_MAGIC, (
            "Downloaded file is not a valid SQLite database"
        )


@pytest.mark.integration
class TestCidTable:
    async def test_cid_table_downloadable_and_parseable(self):
        """6.4 cid_table.json 可下載且為合法 JSON"""
        import json

        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.get(CID_TABLE_URL)

        assert response.status_code == 200, (
            f"cid_table.json download failed with status {response.status_code}"
        )

        data = json.loads(response.text)
        assert isinstance(data, (dict, list)), "cid_table.json is not a dict or list"
        assert len(data) > 0, "cid_table.json is empty"


@pytest.mark.integration
class TestCardImage:
    async def test_known_card_image_accessible(self):
        """6.5 已知卡圖 URL 可存取（用已知 passcode）"""
        image_url = f"{CARD_IMAGE_BASE_URL}{KNOWN_PASSCODE}.jpg"

        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.get(image_url)

        assert response.status_code == 200, (
            f"Card image not accessible: {image_url} returned {response.status_code}"
        )
        content_type = response.headers.get("content-type", "")
        assert "image" in content_type, (
            f"Expected image content-type, got: {content_type}"
        )
