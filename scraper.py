import requests
import pandas as pd
from datetime import datetime
import logging
import json
import time
from fake_useragent import UserAgent
import os
import argparse
import sys
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio
import aiohttp
from typing import List, Dict, Any
import numpy as np

# 設定程式的日誌 (Log) 格式，方便除錯
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 基本設定
BASE_URL = "https://rtapi.ruten.com.tw/api"
IMAGE_BASE_URL = "https://gcs.rimg.com.tw"
DEFAULT_TIMEOUT = 10  # 預設連線超時秒數
DEFAULT_RETRY_DELAY = 1  # 重試連線前的等待秒數
MAX_RETRIES = 3 # 最大重試次數
ITEMS_PER_PAGE = 110 # 每次搜尋抓取的商品數量
DEFAULT_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
MAX_CONCURRENT_REQUESTS = 10  # 同一時間最多可以發送幾個請求 (避免被網站封鎖)

class RutenScraper:
    def __init__(self):
        """初始化爬蟲工具"""
        self.session = requests.Session()
        self.ua = UserAgent()
        
        # 設定連線重試策略，網路不穩時會自動重試
        retry_strategy = Retry(
            total=MAX_RETRIES,
            backoff_factor=0.5,  # 每次重試間隔時間稍微拉長
            status_forcelist=[500, 502, 503, 504], # 遇到這些伺服器錯誤時才重試
            allowed_methods=["GET", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=100, pool_maxsize=100)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # 建立專門放商品圖片的資料夾 (如果不存在的話)
        self.image_dir = "product_images"
        if not os.path.exists(self.image_dir):
            os.makedirs(self.image_dir)
        
    def _get_headers(self):
        """產生偽裝成瀏覽器的標頭資訊 (User-Agent)"""
        try:
            return {
                'User-Agent': self.ua.random, # 隨機選一個瀏覽器身份
                'Accept': 'application/json',
                'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                'Referer': 'https://www.ruten.com.tw/',
                'Connection': 'keep-alive'
            }
        except Exception as e:
            logger.warning(f"無法產生隨機 User-Agent，改用預設值: {e}")
            return {
                'User-Agent': DEFAULT_USER_AGENT,
                'Accept': 'application/json',
                'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                'Referer': 'https://www.ruten.com.tw/',
                'Connection': 'keep-alive'
            }

    async def search_products_async(self, keyword: str, limit: int = ITEMS_PER_PAGE, offset: int = 1) -> tuple:
        """
        [非同步] 搜尋商品
        keyword: 搜尋關鍵字
        limit: 數量限制
        offset: 頁數偏移量
        """
        url = f"{BASE_URL}/search/v3/index.php/core/prod"
        params = {
            'q': keyword,
            'type': 'direct',
            'sort': 'rnk/dc', # 排序方式
            'limit': limit,
            'offset': offset
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=params, headers=self._get_headers(), timeout=DEFAULT_TIMEOUT) as response:
                    result = await response.json()
                    # 檢查實際搜尋到的總數量
                    if result and 'TotalRows' in result:
                        total_rows = result['TotalRows']
                        if total_rows < limit:
                            logger.info(f"搜尋結果只有 {total_rows} 個商品，調整爬取數量")
                            return result, total_rows
                    return result, limit
            except Exception as e:
                logger.error(f"搜尋商品時發生錯誤: {e}")
                return None, 0

    async def get_product_details_async(self, product_ids: List[str]) -> Dict:
        """[非同步] 取得商品的詳細資訊"""
        if isinstance(product_ids, list):
            product_ids = ','.join(product_ids)
            
        url = f"{BASE_URL}/prod/v2/index.php/prod"
        params = {'id': product_ids}
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=params, headers=self._get_headers(), timeout=DEFAULT_TIMEOUT) as response:
                    return await response.json()
            except Exception as e:
                logger.error(f"獲取商品詳情時發生錯誤: {e}")
                return None

    def _extract_product_data(self, product: Dict) -> Dict:
        """從原始資料中提取我們需要的欄位"""
        try:
            # 計算剩餘庫存 (總量 - 已售出)
            remaining_stock = product.get('StockQty', 0) - product.get('SoldQty', 0)
            
            # 處理價格區間
            price_range = product.get('PriceRange', [0])
            price = int(price_range[0]) if price_range and price_range[0] is not None else 0
            
            # 判斷是否有價差 (例如同個商品頁面有多種規格)
            alt_price = 0
            if price_range and len(price_range) > 1 and price_range[0] != price_range[-1]:
                alt_price = 1

            shipping_cost = product.get('ShippingCost')
            shipping_cost = int(shipping_cost) if shipping_cost is not None else 0

            image_url = product.get('Image', '')
            
            return {
                '商品ID': product.get('ProdId', ''),
                '商品名稱': product.get('ProdName', ''),
                '賣家ID': product.get('SellerId', ''),
                '價格': price,
                '是否有價差': alt_price,
                '剩餘數量': remaining_stock,
                '最低運費': shipping_cost,
                '上架時間': product.get('PostTime', ''),
                '圖片連結': image_url
            }
        except Exception as e:
            logger.error(f"處理商品資料時發生錯誤：{e}")
            return None

    async def process_products_async(self, keyword: str, max_pages: int = 999) -> List[Dict]:
        """
        [非同步] 主要處理流程：搜尋 -> 取得詳情 -> 整理資料
        """
        all_products = []
        page = 1
        
        while page <= max_pages:
            try:
                offset = (page - 1) * ITEMS_PER_PAGE + 1
                logger.info(f"正在處理關鍵字 '{keyword}' 的第 {page} 頁")
                
                # 1. 搜尋商品
                search_result, available_items = await self.search_products_async(keyword, limit=ITEMS_PER_PAGE, offset=offset)
                if not search_result or 'Rows' not in search_result or not search_result['Rows']:
                    logger.info(f"關鍵字 '{keyword}' 在第 {page} 頁沒有更多結果了。")
                    break
                
                # 2. 拿到所有商品 ID
                product_ids = [row['Id'] for row in search_result['Rows']]
                
                # 3. 取得詳細資訊
                product_details = await self.get_product_details_async(product_ids)
                if not product_details:
                    break
                
                # 4. 多工處理資料轉換
                with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_REQUESTS) as executor:
                    futures = [executor.submit(self._extract_product_data, product) for product in product_details]
                    for future in as_completed(futures):
                        product_data = future.result()
                        if product_data:
                            all_products.append(product_data)
                
                # 如果這頁不滿，代表沒有下一頁了
                if len(search_result['Rows']) < ITEMS_PER_PAGE:
                    break
                
                page += 1
                await asyncio.sleep(0.5)  # 稍微休息一下，避免請求太頻繁
                
            except Exception as e:
                logger.error(f"處理關鍵字 '{keyword}' 的第 {page} 頁時發生錯誤: {e}")
                break
        
        return all_products

    def save_data(self, data: List[Dict], output_file: str = None) -> None:
        """將爬取到的資料儲存為 CSV 檔案"""
        # 如果沒有指定檔名，就用時間當檔名
        if not output_file:
            output_file = f"ruten_products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        # 確保副檔名是 .csv
        if not output_file.lower().endswith('.csv'):
            output_file += '.csv'
        
        try:
            df = pd.DataFrame(data)
            # 將中文欄位名稱轉換為英文，方便程式處理
            df = df.rename(columns={
                '商品ID': 'product_id',
                '商品名稱': 'product_name',
                '賣家ID': 'seller_id',
                '價格': 'price',
                '是否有價差': 'alt_price',
                '剩餘數量': 'stock_qty',
                '最低運費': 'shipping_cost',
                '上架時間': 'post_time',
                '圖片連結': 'image_url'
            })

            # 調整欄位順序，把 'search_card_name' 移到最前面
            cols = df.columns.tolist()
            if 'search_card_name' in cols:
                cols.insert(0, cols.pop(cols.index('search_card_name')))
                df = df[cols]

            # 存檔 (utf-8-sig 可以讓 Excel 正確顯示中文)
            df.to_csv(output_file, index=False, encoding='utf-8-sig')
            logger.info(f"資料已成功儲存到 {output_file}")
        except Exception as e:
            logger.error(f"儲存資料時發生錯誤：{e}")

async def main_async(cart_path='data/cart.json', output_path=None):
    # 1. 讀取購物車設定
    try:
        with open(cart_path, 'r', encoding='utf-8') as f:
            cart_data = json.load(f)
        shopping_cart = cart_data.get('shopping_cart', [])
        if not shopping_cart:
            print("購物車是空的，沒有東西可以爬取。")
            return
    except FileNotFoundError:
        print(f"錯誤：找不到 '{cart_path}'。請確保檔案存在於正確的路徑。")
        return
    except json.JSONDecodeError:
        print(f"錯誤：'{cart_path}' 格式不正確。")
        return

    # 2. 初始化爬蟲
    scraper = RutenScraper()
    all_products_list = []

    # 3. 逐一搜尋購物車中的卡片
    for item in shopping_cart:
        card_name = item.get('card_name_zh')
        target_ids = item.get('target_ids', [])
        
        if not card_name or not target_ids:
            continue

        for target_id in target_ids:
            print(f"\n開始搜尋卡片：{card_name}, ID: {target_id}")
            
            # 限制最多5頁，避免抓太久
            products = await scraper.process_products_async(target_id, max_pages=5)
            
            # 標記這是哪張卡片的搜尋結果
            for product in products:
                product['search_card_name'] = card_name
            
            all_products_list.extend(products)

    # 4. 確保輸出目錄存在
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
    else:
        # 如果沒指定輸出路徑，就放在預設位置
        os.makedirs('data', exist_ok=True)
        output_path = f"data/ruten_all_cards_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    # 5. 儲存結果
    if all_products_list:
        scraper.save_data(all_products_list, output_file=output_path)
        print(f"\n爬蟲完成！所有資料已儲存至：{output_path}")
    else:
        print("\n爬蟲完成，但沒有找到任何商品。")

def main():
    # 設定命令列參數
    parser = argparse.ArgumentParser(description='露天拍賣爬蟲')
    parser.add_argument('--cart', default='data/cart.json', help='購物車設定檔路徑')
    parser.add_argument('--output', default=None, help='輸出 CSV 檔案路徑')
    args = parser.parse_args()
    
    # 執行非同步主程式
    asyncio.run(main_async(args.cart, args.output))

if __name__ == "__main__":
    main()