"""
app/services/ruten_scraper.py - 露天拍賣爬蟲服務
=================================================
從根目錄 scraper.py 搬移而來，移除 CLI 相關程式碼。
保留 RutenScraper 類別的完整邏輯，並新增 run() 方法供 router 直接呼叫。

功能：根據購物車中的卡片清單，到露天拍賣搜尋商品並儲存為 CSV。
"""
import asyncio
import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Dict, List

import aiohttp
import pandas as pd
import requests
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app.config import RUTEN_API_BASE_URL, RUTEN_BASE_URL, RUTEN_IMAGE_BASE_URL

# 設定日誌
logger = logging.getLogger(__name__)

# 基本設定
BASE_URL = RUTEN_API_BASE_URL
IMAGE_BASE_URL = RUTEN_IMAGE_BASE_URL
DEFAULT_TIMEOUT = 10       # 預設連線超時秒數
DEFAULT_RETRY_DELAY = 1    # 重試連線前的等待秒數
MAX_RETRIES = 3            # 最大重試次數
ITEMS_PER_PAGE = 110       # 每次搜尋抓取的商品數量
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/91.0.4472.124 Safari/537.36"
)
MAX_CONCURRENT_REQUESTS = 10  # 同一時間最多發送幾個請求


class RutenScraper:
    """
    露天拍賣爬蟲。

    使用方法（直接呼叫）：
        scraper = RutenScraper()
        await scraper.run(
            cart_path="data/project/cart.json",
            output_path="data/project/ruten_data.csv"
        )
    """

    def __init__(self):
        """初始化爬蟲工具"""
        self.session = requests.Session()
        self.ua = UserAgent()

        # 設定連線重試策略，網路不穩時會自動重試
        retry_strategy = Retry(
            total=MAX_RETRIES,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )
        adapter = HTTPAdapter(
            max_retries=retry_strategy, pool_connections=100, pool_maxsize=100
        )
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # 建立商品圖片資料夾
        self.image_dir = "product_images"
        if not os.path.exists(self.image_dir):
            os.makedirs(self.image_dir)

    def _get_headers(self):
        """產生偽裝成瀏覽器的標頭資訊（隨機 User-Agent）"""
        try:
            return {
                "User-Agent": self.ua.random,
                "Accept": "application/json",
                "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                "Referer": f"{RUTEN_BASE_URL}/",
                "Connection": "keep-alive",
            }
        except Exception as e:
            logger.warning(f"無法產生隨機 User-Agent，改用預設值: {e}")
            return {
                "User-Agent": DEFAULT_USER_AGENT,
                "Accept": "application/json",
                "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                "Referer": f"{RUTEN_BASE_URL}/",
                "Connection": "keep-alive",
            }

    async def _search_products_async(
        self, keyword: str, limit: int = ITEMS_PER_PAGE, offset: int = 1
    ) -> tuple:
        """
        [非同步] 搜尋商品。

        Args:
            keyword: 搜尋關鍵字
            limit: 數量限制
            offset: 頁數偏移量

        Returns:
            tuple: (搜尋結果 dict, 實際可用數量)
        """
        url = f"{BASE_URL}/search/v3/index.php/core/prod"
        params = {
            "q": keyword,
            "type": "direct",
            "sort": "rnk/dc",
            "limit": limit,
            "offset": offset,
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    url,
                    params=params,
                    headers=self._get_headers(),
                    timeout=DEFAULT_TIMEOUT,
                ) as response:
                    result = await response.json()
                    if result and "TotalRows" in result:
                        total_rows = result["TotalRows"]
                        if total_rows < limit:
                            logger.info(
                                f"搜尋結果只有 {total_rows} 個商品，調整爬取數量"
                            )
                            return result, total_rows
                    return result, limit
            except Exception as e:
                logger.error(f"搜尋商品時發生錯誤: {e}")
                return None, 0

    async def _get_product_details_async(self, product_ids: List[str]) -> Dict:
        """[非同步] 取得商品的詳細資訊"""
        if isinstance(product_ids, list):
            product_ids = ",".join(product_ids)

        url = f"{BASE_URL}/prod/v2/index.php/prod"
        params = {"id": product_ids}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    url,
                    params=params,
                    headers=self._get_headers(),
                    timeout=DEFAULT_TIMEOUT,
                ) as response:
                    return await response.json()
            except Exception as e:
                logger.error(f"獲取商品詳情時發生錯誤: {e}")
                return None

    def _extract_product_data(self, product: Dict) -> Dict:
        """從原始資料中提取我們需要的欄位"""
        try:
            remaining_stock = product.get("StockQty", 0) - product.get("SoldQty", 0)

            price_range = product.get("PriceRange", [0])
            price = (
                int(price_range[0])
                if price_range and price_range[0] is not None
                else 0
            )

            alt_price = 0
            if (
                price_range
                and len(price_range) > 1
                and price_range[0] != price_range[-1]
            ):
                alt_price = 1

            shipping_cost = product.get("ShippingCost")
            shipping_cost = int(shipping_cost) if shipping_cost is not None else 0

            image_url = product.get("Image", "")

            return {
                "商品ID": product.get("ProdId", ""),
                "商品名稱": product.get("ProdName", ""),
                "賣家ID": product.get("SellerId", ""),
                "價格": price,
                "是否有價差": alt_price,
                "剩餘數量": remaining_stock,
                "最低運費": shipping_cost,
                "上架時間": product.get("PostTime", ""),
                "圖片連結": image_url,
            }
        except Exception as e:
            logger.error(f"處理商品資料時發生錯誤：{e}")
            return None

    async def _process_products_async(
        self, keyword: str, max_pages: int = 999
    ) -> List[Dict]:
        """[非同步] 主要處理流程：搜尋 → 取得詳情 → 整理資料"""
        all_products = []
        page = 1

        while page <= max_pages:
            try:
                offset = (page - 1) * ITEMS_PER_PAGE + 1
                logger.info(f"正在處理關鍵字 '{keyword}' 的第 {page} 頁")

                # 搜尋商品
                search_result, available_items = await self._search_products_async(
                    keyword, limit=ITEMS_PER_PAGE, offset=offset
                )
                if (
                    not search_result
                    or "Rows" not in search_result
                    or not search_result["Rows"]
                ):
                    logger.info(f"關鍵字 '{keyword}' 在第 {page} 頁沒有更多結果了。")
                    break

                # 拿到所有商品 ID
                product_ids = [row["Id"] for row in search_result["Rows"]]

                # 取得詳細資訊
                product_details = await self._get_product_details_async(product_ids)
                if not product_details:
                    break

                # 多工處理資料轉換
                with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_REQUESTS) as executor:
                    futures = [
                        executor.submit(self._extract_product_data, product)
                        for product in product_details
                    ]
                    for future in as_completed(futures):
                        product_data = future.result()
                        if product_data:
                            all_products.append(product_data)

                # 如果這頁不滿，代表沒有下一頁了
                if len(search_result["Rows"]) < ITEMS_PER_PAGE:
                    break

                page += 1
                await asyncio.sleep(0.5)

            except Exception as e:
                logger.error(
                    f"處理關鍵字 '{keyword}' 的第 {page} 頁時發生錯誤: {e}"
                )
                break

        return all_products

    def _save_data(self, data: List[Dict], output_file: str) -> None:
        """將爬取到的資料儲存為 CSV 檔案"""
        if not output_file:
            output_file = f"ruten_products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        if not output_file.lower().endswith(".csv"):
            output_file += ".csv"

        try:
            df = pd.DataFrame(data)
            # 將中文欄位名稱轉換為英文
            df = df.rename(
                columns={
                    "商品ID": "product_id",
                    "商品名稱": "product_name",
                    "賣家ID": "seller_id",
                    "價格": "price",
                    "是否有價差": "alt_price",
                    "剩餘數量": "stock_qty",
                    "最低運費": "shipping_cost",
                    "上架時間": "post_time",
                    "圖片連結": "image_url",
                }
            )

            # 調整欄位順序，把 'search_card_name' 移到最前面
            cols = df.columns.tolist()
            if "search_card_name" in cols:
                cols.insert(0, cols.pop(cols.index("search_card_name")))
                df = df[cols]

            # 存檔（utf-8-sig 讓 Excel 正確顯示中文）
            df.to_csv(output_file, index=False, encoding="utf-8-sig")
            logger.info(f"資料已成功儲存到 {output_file}")
        except Exception as e:
            logger.error(f"儲存資料時發生錯誤：{e}")
            raise RuntimeError(f"儲存爬蟲結果失敗: {e}")

    async def run(self, cart_path: str, output_path: str) -> None:
        """
        執行完整的露天拍賣爬蟲流程。

        依序：
        1. 讀取購物車設定
        2. 逐一搜尋購物車中的卡片
        3. 儲存結果為 CSV

        Args:
            cart_path: 購物車 JSON 路徑
            output_path: 輸出 CSV 路徑

        Raises:
            FileNotFoundError: 找不到購物車設定檔
            RuntimeError: 爬蟲過程中發生錯誤
        """
        # 1. 讀取購物車設定
        try:
            with open(cart_path, "r", encoding="utf-8") as f:
                cart_data = json.load(f)
            shopping_cart = cart_data.get("shopping_cart", [])
            if not shopping_cart:
                raise RuntimeError("購物車是空的，沒有東西可以爬取。")
        except FileNotFoundError:
            raise FileNotFoundError(f"找不到購物車設定檔: {cart_path}")
        except json.JSONDecodeError:
            raise RuntimeError(f"購物車設定檔格式不正確: {cart_path}")

        # 2. 逐一搜尋購物車中的卡片
        all_products_list = []

        for item in shopping_cart:
            card_name = item.get("card_name_zh")
            target_card_numbers = item.get("target_card_numbers", [])

            if not card_name or not target_card_numbers:
                continue

            for target_card_number in target_card_numbers:
                # target_card_numbers 可能是純字串 "DABL-JP035"
                # 或是字典 {"card_number": "DABL-JP035", "rarity_name": "...", ...}
                if isinstance(target_card_number, dict):
                    card_number_str = target_card_number.get("card_number", "")
                else:
                    card_number_str = str(target_card_number)

                if not card_number_str:
                    continue

                logger.info(f"開始搜尋卡片：{card_name}, ID: {card_number_str}")

                # 限制最多 5 頁，避免抓太久
                products = await self._process_products_async(
                    card_number_str, max_pages=5
                )

                # 標記這是哪張卡片的搜尋結果
                for product in products:
                    product["search_card_name"] = card_name

                all_products_list.extend(products)

        # 3. 儲存結果
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        if all_products_list:
            self._save_data(all_products_list, output_file=output_path)
            logger.info(f"爬蟲完成！所有資料已儲存至：{output_path}")
        else:
            # 即使沒結果也建立空 CSV，讓後續流程不會因找不到檔案而失敗
            logger.warning("爬蟲完成，但沒有找到任何商品。建立空白 CSV。")
            pd.DataFrame().to_csv(output_path, index=False, encoding="utf-8-sig")
