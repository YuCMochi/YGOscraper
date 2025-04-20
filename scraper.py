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
from requests.packages.urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio
import aiohttp
from typing import List, Dict, Any
import numpy as np

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 常數定義
BASE_URL = "https://rtapi.ruten.com.tw/api"
IMAGE_BASE_URL = "https://gcs.rimg.com.tw"
DEFAULT_TIMEOUT = 10
DEFAULT_RETRY_DELAY = 1  # 減少重試延遲
MAX_RETRIES = 3
ITEMS_PER_PAGE = 110
DEFAULT_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
MAX_CONCURRENT_REQUESTS = 10  # 最大並行請求數

class RutenScraper:
    def __init__(self):
        self.session = requests.Session()
        self.ua = UserAgent()
        
        # 優化重試機制
        retry_strategy = Retry(
            total=MAX_RETRIES,
            backoff_factor=0.5,  # 減少重試間隔
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=100, pool_maxsize=100)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # 建立圖片儲存目錄
        self.image_dir = "product_images"
        if not os.path.exists(self.image_dir):
            os.makedirs(self.image_dir)
        
        # 初始化快取
        self.product_cache = {}
        self.session_cache = {}

    def _get_headers(self):
        """生成隨機的 User-Agent"""
        try:
            return {
                'User-Agent': self.ua.random,
                'Accept': 'application/json',
                'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                'Referer': 'https://www.ruten.com.tw/',
                'Connection': 'keep-alive'
            }
        except Exception as e:
            logger.warning(f"生成 User-Agent 時發生錯誤，使用預設值: {e}")
            return {
                'User-Agent': DEFAULT_USER_AGENT,
                'Accept': 'application/json',
                'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                'Referer': 'https://www.ruten.com.tw/',
                'Connection': 'keep-alive'
            }

    async def search_products_async(self, keyword: str, limit: int = ITEMS_PER_PAGE, offset: int = 1) -> tuple:
        """非同步搜尋商品"""
        url = f"{BASE_URL}/search/v3/index.php/core/prod"
        params = {
            'q': keyword,
            'type': 'direct',
            'sort': 'rnk/dc',
            'limit': limit,
            'offset': offset
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=params, headers=self._get_headers(), timeout=DEFAULT_TIMEOUT) as response:
                    result = await response.json()
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
        """非同步獲取商品詳細資訊"""
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
        """從商品資料中提取所需資訊"""
        try:
            remaining_stock = product.get('StockQty', 0) - product.get('SoldQty', 0)
            price_range = product.get('PriceRange', [0])
            image_url = product.get('Image', '')
            
            return {
                '商品ID': product.get('ProdId', ''),
                '商品名稱': product.get('ProdName', ''),
                '賣家ID': product.get('SellerId', ''),
                '價格': int(price_range[0]),
                '剩餘數量': remaining_stock,
                '最低運費': int(product.get('ShippingCost', 0)),
                '上架時間': product.get('PostTime', ''),
                '圖片連結': image_url
            }
        except Exception as e:
            logger.error(f"處理商品資料時發生錯誤：{e}")
            return None

    async def process_products_async(self, keyword: str) -> List[Dict]:
        """非同步處理商品資料"""
        all_products = []
        page = 1
        
        while True:
            try:
                offset = (page - 1) * ITEMS_PER_PAGE + 1
                logger.info(f"正在處理第 {page} 頁")
                
                # 非同步搜尋商品
                search_result, available_items = await self.search_products_async(keyword, limit=ITEMS_PER_PAGE, offset=offset)
                if not search_result or 'Rows' not in search_result:
                    break
                
                # 獲取商品ID列表
                product_ids = [row['Id'] for row in search_result['Rows']]
                
                # 非同步獲取商品詳情
                product_details = await self.get_product_details_async(product_ids)
                if not product_details:
                    break
                
                # 並行處理商品資料
                with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_REQUESTS) as executor:
                    futures = [executor.submit(self._extract_product_data, product) for product in product_details]
                    for future in as_completed(futures):
                        product_data = future.result()
                        if product_data:
                            all_products.append(product_data)
                
                if len(search_result['Rows']) < ITEMS_PER_PAGE:
                    break
                
                page += 1
                await asyncio.sleep(0.5)  # 減少請求間隔
                
            except Exception as e:
                logger.error(f"處理第 {page} 頁時發生錯誤: {e}")
                break
        
        return all_products

    def save_data(self, data: List[Dict], filename: str = None) -> None:
        """儲存爬取的資料"""
        if not filename:
            filename = f"ruten_products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        if not filename.lower().endswith('.csv'):
            filename += '.csv'
        
        try:
            df = pd.DataFrame(data)
            df = df.rename(columns={
                '商品ID': 'product_id',
                '商品名稱': 'product_name',
                '賣家ID': 'seller_id',
                '價格': 'price',
                '剩餘數量': 'stock_qty',
                '最低運費': 'shipping_cost',
                '上架時間': 'post_time',
                '圖片連結': 'image_url'
            })
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            logger.info(f"資料已成功儲存到 {filename}")
        except Exception as e:
            logger.error(f"儲存資料時發生錯誤：{e}")

async def main_async():
    # 檢查是否有命令列參數
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(description='露天拍賣商品爬蟲')
        parser.add_argument('-k', '--keyword', type=str, required=True, help='搜尋關鍵字')
        parser.add_argument('-o', '--output', type=str, help='輸出檔案名稱（選填）')
        args = parser.parse_args()
        keyword, output = args.keyword, args.output
    else:
        print("\n=== 露天拍賣商品爬蟲 ===")
        print("請輸入以下資訊：")
        while True:
            keyword = input("\n請輸入搜尋關鍵字：").strip()
            if keyword:
                break
            print("關鍵字不能為空，請重新輸入！")
        output = input("請輸入輸出檔案名稱（選填，直接按Enter使用預設名稱）：").strip()
    
    # 初始化爬蟲
    scraper = RutenScraper()
    
    # 執行爬蟲
    print(f"\n開始搜尋關鍵字：{keyword}")
    products = await scraper.process_products_async(keyword)
    
    # 儲存資料
    if output:
        output_file = output
    else:
        output_file = f"ruten_{keyword}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    scraper.save_data(products, output_file)
    print(f"\n爬蟲完成！資料已儲存至：{output_file}")

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main() 