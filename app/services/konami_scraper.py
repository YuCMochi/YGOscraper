"""
app/services/konami_scraper.py - Konami 官方資料庫爬蟲
======================================================
從根目錄 konami_scraper.py 搬移而來，移除 CLI 相關程式碼。
保留 KonamiScraper 類別的完整邏輯。

功能：根據 CID（Konami 卡片 ID）爬取該卡片的所有版本卡號與稀有度。
"""
import logging
import random
import re
import time

import requests
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app.config import KONAMI_DB_BASE_URL

# 設定日誌格式，方便追蹤程式執行狀況與錯誤
logger = logging.getLogger(__name__)

# 基本設定
MAX_RETRIES = 3  # 最大重試次數


class KonamiScraper:
    """
    Konami 官方卡片資料庫爬蟲。

    使用方法：
        scraper = KonamiScraper()
        results = scraper.scrape_cids(["4007", "4008"])
        # results = {"4007": [{"card_number": "DABL-JP035", ...}, ...], ...}
    """

    def __init__(self):
        """初始化爬蟲工具，設定 Session 與重試機制，模擬真實使用者行為"""
        self.session = requests.Session()
        self.ua = UserAgent()

        # 設定連線重試策略，當遇到 500, 502, 503, 504 錯誤時自動重試
        retry_strategy = Retry(
            total=MAX_RETRIES,
            backoff_factor=1,  # 每次重試間隔時間 (秒)
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _get_headers(self):
        """產生隨機的 User-Agent 與標準標頭，以偽裝成真實瀏覽器"""
        try:
            return {
                "User-Agent": self.ua.random,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "ja,en-US;q=0.7,en;q=0.3",
                "Referer": "https://www.db.yugioh-card.com/",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }
        except Exception as e:
            logger.warning(f"無法產生隨機 User-Agent，使用預設值: {e}")
            return {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept-Language": "ja",
            }

    def fetch_data(self, cid):
        """
        抓取指定 CID 的 Konami 網頁資料。

        Args:
            cid (str): Konami Card ID (例如: "4006")

        Returns:
            str: 網頁 HTML 內容，若失敗則回傳 None
        """
        url = f"{KONAMI_DB_BASE_URL}?ope=2&cid={cid}&request_locale=ja"
        logger.info(f"正在抓取 CID: {cid} - URL: {url}")

        try:
            # 加入隨機延遲 (1~3秒)，避免被伺服器視為惡意攻擊
            delay = random.uniform(1, 3)
            time.sleep(delay)

            response = self.session.get(url, headers=self._get_headers(), timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"抓取 CID {cid} 時發生錯誤: {e}")
            return None

    def parse_html(self, html_content):
        """
        解析 HTML 內容並提取卡片版本資訊。

        Args:
            html_content (str): 網頁 HTML 內容

        Returns:
            list: 包含卡片版本資訊的字典列表
        """
        versions = []

        if not html_content:
            return versions

        # 尋找版本列表區塊 (CardDetail_packlist)
        packlist_match = re.search(
            r"<!-- ///CardDetail_packlist  -->(.*?)<!-- ///",
            html_content,
            re.DOTALL,
        )
        if not packlist_match:
            # 備用方案：某些頁面結構可能不同
            packlist_match = re.search(
                r'<div id="update_list" class="list">(.*?)</div>\s*</div>\s*<!-- \.icon -->',
                html_content,
                re.DOTALL,
            )

        # 決定要搜尋的內容範圍
        content_to_search = packlist_match.group(1) if packlist_match else html_content

        # 尋找每一列 (t_row)
        row_pattern = re.compile(
            r'<div class="t_row\s*"(.*?)>\s*(.*?)\s*</div>\s*</div>\s*<!-- \.icon -->',
            re.DOTALL,
        )

        for row_match in row_pattern.finditer(content_to_search):
            row_html = row_match.group(2)

            # 提取卡片編號 (Card Number)
            card_num_match = re.search(
                r'<div class="card_number">\s*(.*?)\s*</div>', row_html, re.DOTALL
            )
            card_number = card_num_match.group(1).strip() if card_num_match else ""

            # 提取卡包名稱 (Pack Name)
            pack_name_match = re.search(
                r'<div class="pack_name flex_1"\s*>\s*(.*?)\s*</div>',
                row_html,
                re.DOTALL,
            )
            pack_name = pack_name_match.group(1).strip() if pack_name_match else ""

            # 提取稀有度 ID 與名稱 (Rarity)
            rarity_id = ""
            rarity_name = ""

            rid_match = re.search(r"rid_(\d+)", row_html)
            if rid_match:
                rarity_id = rid_match.group(1)

                # 簡稱位於 <p> 標籤內 (例如 UR)
                p_match = re.search(r"<p>(.*?)</p>", row_html)
                short_name = p_match.group(1).strip() if p_match else ""

                # 完整名稱位於 <span> 標籤內
                span_match = re.search(
                    r"<span[^>]*>\s*(.*?)\s*</span>", row_html, re.DOTALL
                )
                full_name = span_match.group(1).strip() if span_match else ""

                if short_name and full_name:
                    rarity_name = f"{short_name} ({full_name})"
                else:
                    rarity_name = short_name or full_name

            versions.append(
                {
                    "card_number": card_number,
                    "pack_name": pack_name,
                    "rarity_id": rarity_id,
                    "rarity_name": rarity_name,
                }
            )

        return versions

    def scrape_cids(self, cids):
        """
        處理多個 CID 的抓取流程。

        Args:
            cids (list): CID 列表 (例如: ["4007", "4008"])

        Returns:
            dict: {cid: [versions]} 格式的結果
        """
        results = {}
        total = len(cids)

        for index, cid in enumerate(cids, 1):
            logger.info(f"進度 ({index}/{total}): 正在處理 CID {cid}")
            html = self.fetch_data(cid)
            if html:
                versions = self.parse_html(html)
                results[cid] = versions
                logger.info(f"CID {cid} 成功提取 {len(versions)} 個版本")
            else:
                results[cid] = []
                logger.warning(f"CID {cid} 抓取失敗或無資料")

        return results
