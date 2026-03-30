"""
app/services/konami_scraper_service.py - Konami 爬蟲的薄包裝層
================================================================
這個薄包裝層（Thin Wrapper）讓 routers 可以透過乾淨的介面呼叫 KonamiScraper，
而不需要直接接觸底層的爬蟲細節。

原始邏輯已搬移至 app/services/konami_scraper.py（KonamiScraper 類別）。
"""
from app.services.konami_scraper import KonamiScraper


class KonamiScraperService:
    """
    Konami 卡片資料庫爬蟲的服務介面。
    
    使用方法：
        service = KonamiScraperService()
        card_numbers = service.get_card_numbers(4007)
    """

    def __init__(self):
        self._scraper = KonamiScraper()

    def get_card_numbers(self, cid: int) -> list[dict]:
        """
        根據 CID 爬取卡片的所有版本卡號清單。

        Args:
            cid: Konami 官方資料庫的卡片 ID（整數）

        Returns:
            包含版本資訊的 list，每項為：
            {"card_number": str, "rarity_name": str, "pack_name": str}
        """
        data = self._scraper.scrape_cids([str(cid)])

        card_numbers = []
        if data and str(cid) in data:
            for v in data[str(cid)]:
                if v.get("card_number"):
                    card_numbers.append(
                        {
                            "card_number": v["card_number"],
                            "rarity_id": v.get("rarity_id", ""),
                            "pack_name": v.get("pack_name", ""),
                        }
                    )

        return card_numbers
